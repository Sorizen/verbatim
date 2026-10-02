from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import settings
from app.db import create_engine, create_session_factory
from app.enums import RunStatus
from app.exceptions import PipelineError, RunNotFoundError
from app.models import Run
from app.pipeline.agents import build_crew
from app.pipeline.budget import Budget
from app.pipeline.execution import ExecutionResult, graph_config, interpret_result
from app.pipeline.graph import PipelineContext, PipelineState, build_graph
from app.pipeline.reporting import DbStepReporter
from app.pipeline.storage import RunWorkspace
from app.providers import open_providers
from app.repository import RunRepository

UNEXPECTED_ERROR = 'unexpected error: {error}'

type GraphInput = PipelineState | Command[bool] | None


@asynccontextmanager
async def worker_sessions() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_engine(pooled=False)
    try:
        yield create_session_factory(engine)
    finally:
        await engine.dispose()


@asynccontextmanager
async def open_checkpointer() -> AsyncIterator[AsyncPostgresSaver]:
    async with AsyncPostgresSaver.from_conn_string(settings.CHECKPOINTER_CONNINFO) as saver:
        await saver.setup()
        yield saver


async def load_run(sessions: async_sessionmaker[AsyncSession], run_id: str) -> Run:
    async with sessions() as session:
        run = await RunRepository(session).get_by_id(run_id)
        if not run:
            raise RunNotFoundError()
        return run


async def save_status(
    sessions: async_sessionmaker[AsyncSession],
    run_id: str,
    status: RunStatus,
    *,
    review_reason: str | None = None,
    error: str | None = None,
    video_path: str | None = None,
) -> None:
    async with sessions() as session:
        await RunRepository(session).mark_status(
            run_id, status, review_reason=review_reason, error=error, video_path=video_path
        )
        await session.commit()


async def save_result(sessions: async_sessionmaker[AsyncSession], run_id: str, result: ExecutionResult) -> None:
    await save_status(
        sessions,
        run_id,
        result.status,
        review_reason=result.review_reason,
        video_path=result.final_video.name if result.final_video else None,
    )


async def invoke_graph(
    sessions: async_sessionmaker[AsyncSession],
    run_id: str,
    graph_input: GraphInput,
    budget: Budget,
) -> ExecutionResult:
    workspace = RunWorkspace.for_run(settings.RUNS_DIR, run_id)
    async with open_providers() as providers, open_checkpointer() as checkpointer:
        graph = build_graph().compile(checkpointer=checkpointer)
        context = PipelineContext(
            run_id=run_id,
            workspace=workspace,
            providers=providers,
            crew=build_crew(providers.llm),
            reporter=DbStepReporter(sessions, run_id, budget),
            budget=budget,
            resolution=settings.VIDEO_RESOLUTION,
        )
        result = await graph.ainvoke(graph_input, config=graph_config(run_id), context=context)
    return interpret_result(result, workspace)


async def execute(sessions: async_sessionmaker[AsyncSession], run: Run, graph_input: GraphInput) -> None:
    budget = Budget(settings.MAX_USD_PER_RUN, run.cost_usd)
    try:
        result = await invoke_graph(sessions, run.id, graph_input, budget)
    except PipelineError as error:
        await save_status(sessions, run.id, RunStatus.FAILED, error=error.message)
        return
    except Exception as error:
        await save_status(sessions, run.id, RunStatus.FAILED, error=UNEXPECTED_ERROR.format(error=error))
        raise
    await save_result(sessions, run.id, result)


async def start_run(run_id: str) -> None:
    async with worker_sessions() as sessions:
        run = await load_run(sessions, run_id)
        await execute(sessions, run, PipelineState(run_id=run.id, idea=run.idea))


async def resume_run(run_id: str, *, approve: bool) -> None:
    async with worker_sessions() as sessions:
        run = await load_run(sessions, run_id)
        await execute(sessions, run, Command(resume=approve))


async def continue_run(run_id: str) -> None:
    async with worker_sessions() as sessions:
        run = await load_run(sessions, run_id)
        await execute(sessions, run, None)
