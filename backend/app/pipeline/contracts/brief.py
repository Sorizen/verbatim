from typing import Self

from pydantic import Field, model_validator

from app.constants import ADULT_AGE, CHARACTER_ID_PATTERN, MAX_CHARACTERS, MAX_SCENE_SECONDS, MIN_SCENE_SECONDS
from app.enums import AssumptionSource, Genre, TimeOfDay, Tone
from app.pipeline.contracts.base import Contract


class BriefSetting(Contract):
    place: str = Field(description='Concrete location in one short phrase')
    time_of_day: TimeOfDay
    era: str = Field(description='Period and region, for example "1880s American frontier"')


class BriefCharacter(Contract):
    id: str = Field(pattern=CHARACTER_ID_PATTERN, description='c1, c2 or c3 in order of appearance')
    name: str
    role: str = Field(description='Function in the scene, for example "the provoker"')
    age: int = Field(ge=ADULT_AGE, description='Every character is a fictional adult')


class Assumption(Contract):
    field: str
    value: str
    source: AssumptionSource


class BriefDraft(Contract):
    logline: str = Field(description='The whole scene in one sentence')
    genre: Genre
    tone: Tone
    setting: BriefSetting
    characters: list[BriefCharacter] = Field(min_length=1, max_length=MAX_CHARACTERS)
    target_duration_s: int = Field(ge=MIN_SCENE_SECONDS, le=MAX_SCENE_SECONDS)
    assumptions: list[Assumption]

    @model_validator(mode='after')
    def _check_unique_character_ids(self) -> Self:
        ids = [character.id for character in self.characters]
        if len(ids) != len(set(ids)):
            raise ValueError('character ids must be unique')
        return self


class Brief(BriefDraft):
    locked_lines: list[str]
