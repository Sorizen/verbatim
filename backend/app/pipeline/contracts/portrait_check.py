from pydantic import Field

from app.constants import PORTRAIT_MAX_SCORE, PORTRAIT_MIN_SCORE
from app.enums import PortraitVerdict
from app.pipeline.contracts.base import Contract


class PortraitScores(Contract):
    description_match: int = Field(ge=PORTRAIT_MIN_SCORE, le=PORTRAIT_MAX_SCORE)
    single_subject: int = Field(ge=PORTRAIT_MIN_SCORE, le=PORTRAIT_MAX_SCORE)
    adult: int = Field(ge=PORTRAIT_MIN_SCORE, le=PORTRAIT_MAX_SCORE)
    clean_frame: int = Field(ge=PORTRAIT_MIN_SCORE, le=PORTRAIT_MAX_SCORE)
    face_integrity: int = Field(ge=PORTRAIT_MIN_SCORE, le=PORTRAIT_MAX_SCORE)
    reference_quality: int = Field(ge=PORTRAIT_MIN_SCORE, le=PORTRAIT_MAX_SCORE)

    def as_dict(self) -> dict[str, int]:
        return self.model_dump()


class PortraitExplanations(Contract):
    description_match: str
    single_subject: str
    adult: str
    clean_frame: str
    face_integrity: str
    reference_quality: str


class PortraitReview(Contract):
    scores: PortraitScores
    explanations: PortraitExplanations


class PortraitCheck(Contract):
    character_id: str
    attempt: int
    portrait_path: str
    review: PortraitReview
    verdict: PortraitVerdict


class PortraitsCheck(Contract):
    round: int
    checks: list[PortraitCheck]
