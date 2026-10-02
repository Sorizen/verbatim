from app.constants import VIDEO_USD_PER_SECOND
from app.enums import VideoResolution
from app.exceptions import BudgetExceededError

OVER_BUDGET_TEMPLATE = 'the next call would cost about ${estimate:.2f}, ${spent:.2f} of ${limit:.2f} is already spent'


def estimate_video_cost(resolution: VideoResolution, duration_s: int) -> float:
    return VIDEO_USD_PER_SECOND[resolution] * duration_s


class Budget:
    def __init__(self, limit_usd: float, spent_usd: float = 0.0) -> None:
        self.limit_usd = limit_usd
        self.spent_usd = spent_usd

    def ensure_room(self, estimate_usd: float) -> None:
        if self.spent_usd + estimate_usd > self.limit_usd:
            raise BudgetExceededError(
                OVER_BUDGET_TEMPLATE.format(estimate=estimate_usd, spent=self.spent_usd, limit=self.limit_usd)
            )

    def record(self, cost_usd: float) -> None:
        self.spent_usd += cost_usd
