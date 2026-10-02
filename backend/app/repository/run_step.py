from datetime import UTC, datetime

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import StepName, StepStatus
from app.models import RunStep


class RunStepRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def start(self, run_id: str, name: StepName, attempt: int) -> RunStep:
        step = RunStep(run_id=run_id, name=name, status=StepStatus.RUNNING, attempt=attempt, cost_usd=0.0)
        self.db.add(step)
        await self.db.flush()
        return step

    async def finish(self, step_id: str, status: StepStatus, *, detail: str | None, cost_usd: float) -> None:
        await self.db.execute(
            update(RunStep)
            .where(RunStep.id == step_id)
            .values(status=status, detail=detail, cost_usd=cost_usd, finished_at=datetime.now(UTC))
        )
