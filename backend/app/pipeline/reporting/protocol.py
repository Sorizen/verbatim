from contextlib import AbstractAsyncContextManager
from typing import Protocol

from app.enums import StepName
from app.pipeline.reporting.handle import StepHandle


class StepReporter(Protocol):
    def step(self, name: StepName, attempt: int = 1) -> AbstractAsyncContextManager[StepHandle]: ...
