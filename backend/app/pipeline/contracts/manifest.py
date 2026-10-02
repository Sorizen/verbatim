from app.enums import RunStatus
from app.pipeline.contracts.base import Contract


class Manifest(Contract):
    run_id: str
    idea: str
    status: RunStatus
    final_path: str | None
    best_attempt: int | None
    models: dict[str, str]
    cost_usd: float
    review_reason: str | None
