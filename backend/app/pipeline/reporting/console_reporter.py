import sys
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.enums import StepName, StepStatus
from app.pipeline.budget import Budget
from app.pipeline.reporting.handle import StepHandle

LINE_TEMPLATE = '{name:<15} #{attempt}  {status:<9} {seconds:6.1f}s  ${cost:.3f}  {detail}'


class ConsoleStepReporter:
    def __init__(self, budget: Budget) -> None:
        self._budget = budget

    @asynccontextmanager
    async def step(self, name: StepName, attempt: int = 1) -> AsyncIterator[StepHandle]:
        started = time.monotonic()
        handle = StepHandle()
        try:
            yield handle
        except Exception as error:
            self._print(name, attempt, StepStatus.FAILED, started, handle.cost_usd, str(error))
            raise
        self._print(name, attempt, handle.status, started, handle.cost_usd, handle.detail or '')

    def _print(
        self,
        name: StepName,
        attempt: int,
        status: StepStatus,
        started: float,
        cost_usd: float,
        detail: str,
    ) -> None:
        self._budget.record(cost_usd)
        line = LINE_TEMPLATE.format(
            name=name.value,
            attempt=attempt,
            status=status.value,
            seconds=time.monotonic() - started,
            cost=cost_usd,
            detail=detail,
        )
        sys.stdout.write(line + '\n')
        sys.stdout.flush()
