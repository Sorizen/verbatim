from typing import Self

from pydantic import Field, model_validator

from app.constants import MAX_OWN_LINE_WORDS, MAX_SHOT_SECONDS, MAX_SHOTS, MIN_SHOT_SECONDS, SHOT_ID_PATTERN
from app.pipeline.contracts.base import Contract


class LineDraft(Contract):
    speaker: str = Field(description='Character id from the brief')
    text: str | None = Field(
        description=(
            f'Your own line in English, at most {MAX_OWN_LINE_WORDS} words; null when the shot uses a locked line'
        )
    )
    locked_line_index: int | None = Field(description='Index of a locked line from the brief; null for your own line')
    emotion: str

    @model_validator(mode='after')
    def _check_single_source(self) -> Self:
        has_text = bool(self.text and self.text.strip())
        has_locked = self.locked_line_index is not None
        if has_text == has_locked:
            raise ValueError('set exactly one of text or locked_line_index')
        return self


class ShotDraft(Contract):
    id: str = Field(pattern=SHOT_ID_PATTERN, description='s1, s2, s3 or s4 in order')
    beat: str = Field(description='What happens in the shot, one sentence')
    duration_s: int = Field(ge=MIN_SHOT_SECONDS, le=MAX_SHOT_SECONDS)
    line: LineDraft | None


class ScriptDraft(Contract):
    title: str
    shots: list[ShotDraft] = Field(min_length=1, max_length=MAX_SHOTS)


class Line(Contract):
    speaker: str
    text: str
    emotion: str
    locked: bool


class Shot(Contract):
    id: str
    beat: str
    duration_s: int
    line: Line | None


class Script(Contract):
    title: str
    shots: list[Shot]

    @property
    def total_seconds(self) -> int:
        return sum(shot.duration_s for shot in self.shots)

    @property
    def spoken_shots(self) -> list[Shot]:
        return [shot for shot in self.shots if shot.line]
