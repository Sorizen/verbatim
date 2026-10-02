from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import RunStatus, StepName
from app.models import Run, RunStep
from app.schema import ExampleRun


class RunRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, idea: str) -> Run:
        run = Run(idea=idea, status=RunStatus.QUEUED, cost_usd=0.0)
        self.db.add(run)
        await self.db.flush()
        return run

    async def add_snapshot(self, snapshot: ExampleRun) -> None:
        run = Run(**snapshot.model_dump(exclude={'steps'}))
        run.steps = [RunStep(**step.model_dump()) for step in snapshot.steps]
        self.db.add(run)
        await self.db.flush()

    async def get_by_id(self, run_id: str) -> Run | None:
        return await self.db.scalar(select(Run).where(Run.id == run_id))

    async def list_recent(self, limit: int) -> list[Run]:
        result = await self.db.scalars(select(Run).order_by(Run.created_at.desc()).limit(limit))
        return list(result.all())

    async def mark_step(self, run_id: str, step: StepName) -> None:
        await self.db.execute(update(Run).where(Run.id == run_id).values(status=RunStatus.RUNNING, current_step=step))

    async def add_cost(self, run_id: str, cost_usd: float) -> None:
        await self.db.execute(update(Run).where(Run.id == run_id).values(cost_usd=Run.cost_usd + cost_usd))

    async def mark_status(
        self,
        run_id: str,
        status: RunStatus,
        *,
        review_reason: str | None = None,
        error: str | None = None,
        video_path: str | None = None,
    ) -> None:
        finished_at = None if status in (RunStatus.QUEUED, RunStatus.RUNNING) else datetime.now(UTC)
        await self.db.execute(
            update(Run)
            .where(Run.id == run_id)
            .values(
                status=status,
                review_reason=review_reason,
                error=error,
                video_path=video_path,
                finished_at=finished_at,
            )
        )
