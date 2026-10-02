from typing import Self

from pydantic import Field, model_validator

from app.enums import AmbientLevel, CameraAngle, CameraMovement, ShotSize, TimeOfDay, VideoResolution
from app.pipeline.contracts.base import Contract
from app.pipeline.contracts.guards import ensure_no_quotes


class Camera(Contract):
    size: ShotSize
    movement: CameraMovement
    angle: CameraAngle


class SceneShotDraft(Contract):
    id: str = Field(description='Shot id from the script, same order')
    camera: Camera
    action: str = Field(description='What is visible in the frame, present tense')
    delivery: str | None = Field(
        description='How the line is spoken: pace and intonation; null when the shot has no line'
    )
    sfx: list[str]


class SceneSettingDraft(Contract):
    place: str
    light: str
    ambient_sound: str


class SceneDraft(Contract):
    style: str = Field(description='Photoreal look, light, color and film texture in one phrase')
    setting: SceneSettingDraft
    shots: list[SceneShotDraft]
    negative: list[str] = Field(description='Things the video must not contain')

    @model_validator(mode='after')
    def _check_no_quoted_dialogue(self) -> Self:
        shot_texts = [text for shot in self.shots for text in (shot.action, shot.delivery, *shot.sfx)]
        setting_texts = [self.setting.place, self.setting.light, self.setting.ambient_sound]
        ensure_no_quotes([self.style, *setting_texts, *shot_texts, *self.negative])
        return self


class SceneFormat(Contract):
    aspect: str
    resolution: VideoResolution
    duration_s: int


class SceneCharacter(Contract):
    id: str
    name: str
    look: str
    wardrobe: str
    voice: str
    portrait: str


class SceneSetting(Contract):
    place: str
    time_of_day: TimeOfDay
    light: str
    ambient_sound: str
    ambient_level: AmbientLevel


class Dialogue(Contract):
    speaker: str
    text: str
    delivery: str


class SceneShot(Contract):
    id: str
    duration_s: int
    camera: Camera
    action: str
    dialogue: Dialogue | None
    sfx: list[str]


class Scene(Contract):
    format: SceneFormat
    style: str
    characters: list[SceneCharacter]
    setting: SceneSetting
    shots: list[SceneShot]
    negative: list[str]
