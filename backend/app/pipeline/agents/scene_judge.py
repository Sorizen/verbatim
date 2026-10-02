from dataclasses import dataclass
from pathlib import Path

from app.constants import JPEG_MIME_TYPE, JUDGE_MODEL, SPEECH_AUDIO_FORMAT
from app.enums import AgentRole
from app.pipeline.agents.caller import AgentResult, StructuredCaller
from app.pipeline.contracts import Scene, SceneJudgment
from app.providers.types import AudioPart, ContentPart, ImagePart, TextPart
from app.utils import file_to_base64, file_to_data_url

PORTRAIT_LABEL_TEMPLATE = 'Image {number} is {character_id}.'
WINDOW_LABEL_TEMPLATE = 'Line window for shot {shot_id}: expected speaker {speaker}, {start:.2f}-{end:.2f} s.'


@dataclass(frozen=True)
class JudgeWindow:
    shot_id: str
    speaker: str
    start_s: float
    end_s: float
    frames: list[Path]
    audio: Path


def build_portrait_parts(portraits: dict[str, Path]) -> list[ContentPart]:
    parts: list[ContentPart] = []
    for number, (character_id, path) in enumerate(portraits.items(), start=1):
        parts.append(TextPart(text=PORTRAIT_LABEL_TEMPLATE.format(number=number, character_id=character_id)))
        parts.append(ImagePart(data_url=file_to_data_url(path, JPEG_MIME_TYPE)))
    return parts


def build_window_parts(window: JudgeWindow) -> list[ContentPart]:
    label = WINDOW_LABEL_TEMPLATE.format(
        shot_id=window.shot_id, speaker=window.speaker, start=window.start_s, end=window.end_s
    )
    frames: list[ContentPart] = [ImagePart(data_url=file_to_data_url(frame, JPEG_MIME_TYPE)) for frame in window.frames]
    audio = AudioPart(data_base64=file_to_base64(window.audio), audio_format=SPEECH_AUDIO_FORMAT)
    return [TextPart(text=label), *frames, audio]


class SceneJudge:
    def __init__(self, caller: StructuredCaller) -> None:
        self._caller = caller

    async def judge(
        self,
        *,
        scene: Scene,
        portraits: dict[str, Path],
        windows: list[JudgeWindow],
    ) -> AgentResult[SceneJudgment]:
        media = build_portrait_parts(portraits)
        for window in windows:
            media.extend(build_window_parts(window))
        return await self._caller.call(
            role=AgentRole.SCENE_JUDGE,
            model=JUDGE_MODEL,
            schema=SceneJudgment,
            payload={'scene': scene.model_dump(mode='json', exclude={'characters': {'__all__': {'portrait'}}})},
            media=media,
        )
