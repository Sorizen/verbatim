from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.enums import StepName, StepStatus
from app.pipeline.budget import Budget
from app.pipeline.reporting.handle import StepHandle
from app.repository import RunRepository, RunStepRepository


class DbStepReporter:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession], run_id: str, budget: Budget) -> None:
        self._session_factory = session_factory
        self._run_id = run_id
        self._budget = budget

    @asynccontextmanager
    async def step(self, name: StepName, attempt: int = 1) -> AsyncIterator[StepHandle]:
        step_id = await self._start(name, attempt)
        handle = StepHandle()
        try:
            yield handle
        except Exception as error:
            await self._finish(step_id, StepStatus.FAILED, str(error), handle.cost_usd)
            raise
        await self._finish(step_id, handle.status, handle.detail, handle.cost_usd)

    async def _start(self, name: StepName, attempt: int) -> str:
        async with self._session_factory() as session:
            step = await RunStepRepository(session).start(self._run_id, name, attempt)
            await RunRepository(session).mark_step(self._run_id, name)
            await session.commit()
            return step.id

    async def _finish(self, step_id: str, status: StepStatus, detail: str | None, cost_usd: float) -> None:
        self._budget.record(cost_usd)
        async with self._session_factory() as session:
            await RunStepRepository(session).finish(step_id, status, detail=detail, cost_usd=cost_usd)
            await RunRepository(session).add_cost(self._run_id, cost_usd)
            await session.commit()
