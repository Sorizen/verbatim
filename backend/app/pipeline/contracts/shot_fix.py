from typing import Self

from pydantic import Field, model_validator

from app.constants import MAX_SHOT_SECONDS, MIN_SHOT_SECONDS
from app.enums import AmbientLevel, ShotFixReason
from app.pipeline.contracts.base import Contract
from app.pipeline.contracts.guards import ensure_no_quotes
from app.pipeline.contracts.scene import Camera


class ShotFix(Contract):
    shot_id: str = Field(description='The shot whose line failed the check')
    duration_s: int = Field(
        ge=MIN_SHOT_SECONDS,
        le=MAX_SHOT_SECONDS,
        description='Longer than before when the line was cut off',
    )
    delivery: str = Field(description='Slower and clearer delivery of the same words')
    ambient_level: AmbientLevel = Field(description='Quieter background when speech was drowned out')
    camera: Camera
    reason: ShotFixReason

    @model_validator(mode='after')
    def _check_no_quoted_dialogue(self) -> Self:
        ensure_no_quotes([self.delivery])
        return self
