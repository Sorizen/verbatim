from langgraph.checkpoint.memory import InMemorySaver

from app.config import settings
from app.models.base import generate_id
from app.pipeline.agents import build_crew
from app.pipeline.budget import Budget
from app.pipeline.execution import ExecutionResult, graph_config, interpret_result
from app.pipeline.graph import PipelineContext, PipelineState, build_graph
from app.pipeline.reporting import ConsoleStepReporter
from app.pipeline.storage import RunWorkspace
from app.providers import open_providers


async def run_locally(idea: str) -> tuple[str, ExecutionResult]:
    run_id = generate_id()
    workspace = RunWorkspace.for_run(settings.RUNS_DIR, run_id)
    budget = Budget(settings.MAX_USD_PER_RUN)
    async with open_providers() as providers:
        graph = build_graph().compile(checkpointer=InMemorySaver())
        context = PipelineContext(
            run_id=run_id,
            workspace=workspace,
            providers=providers,
            crew=build_crew(providers.llm),
            reporter=ConsoleStepReporter(budget),
            budget=budget,
            resolution=settings.VIDEO_RESOLUTION,
        )
        result = await graph.ainvoke(
            PipelineState(run_id=run_id, idea=idea), config=graph_config(run_id), context=context
        )
    return run_id, interpret_result(result, workspace)
