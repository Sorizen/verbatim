from app.enums import VideoJobStatus
from app.pipeline.contracts.base import Contract


class RenderAttempt(Contract):
    attempt: int
    model: str
    request_path: str
    seed: int
    job_id: str
    status: VideoJobStatus
    video_path: str | None
    cost_usd: float
