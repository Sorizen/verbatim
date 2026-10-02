from app.enums import StepStatus


class StepHandle:
    def __init__(self) -> None:
        self.status = StepStatus.OK
        self.detail: str | None = None
        self.cost_usd = 0.0

    def add_cost(self, cost_usd: float) -> None:
        self.cost_usd += cost_usd

    def note(self, detail: str) -> None:
        self.detail = detail

    def reject(self, detail: str) -> None:
        self.status = StepStatus.REJECTED
        self.detail = detail
