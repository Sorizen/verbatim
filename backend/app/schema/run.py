from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.enums import RunStatus, StepName, StepStatus


class RunStepSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: StepName
    status: StepStatus
    attempt: int
    detail: str | None
    cost_usd: float
    created_at: datetime
    finished_at: datetime | None


class RunSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    idea: str
    status: RunStatus
    cost_usd: float
    created_at: datetime
    video_url: str | None = None


class RunSchema(RunSummarySchema):
    current_step: StepName | None
    review_reason: str | None
    error: str | None
    updated_at: datetime
    finished_at: datetime | None
    steps: list[RunStepSchema]
    can_continue: bool = False
