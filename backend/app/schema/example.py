from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.enums import RunStatus, StepName, StepStatus


class ExampleStep(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: StepName
    status: StepStatus
    attempt: int
    detail: str | None
    cost_usd: float
    created_at: datetime
    updated_at: datetime
    finished_at: datetime | None


class ExampleRun(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    idea: str
    status: RunStatus
    current_step: StepName | None
    cost_usd: float
    review_reason: str | None
    error: str | None
    video_path: str | None
    created_at: datetime
    updated_at: datetime
    finished_at: datetime | None
    steps: list[ExampleStep]


class ExampleRunsFile(BaseModel):
    runs: list[ExampleRun]
