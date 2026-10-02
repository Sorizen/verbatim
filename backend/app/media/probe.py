from pathlib import Path

from pydantic import BaseModel, ConfigDict

from app.constants import FFPROBE_BINARY
from app.media.process import run_tool

VIDEO_CODEC_TYPE = 'video'
AUDIO_CODEC_TYPE = 'audio'
COMMENT_TAG = 'comment'


class FfprobeStream(BaseModel):
    model_config = ConfigDict(extra='ignore')

    codec_type: str
    width: int | None = None
    height: int | None = None


class FfprobeFormat(BaseModel):
    model_config = ConfigDict(extra='ignore')

    duration: float = 0.0
    tags: dict[str, str] = {}


class FfprobeOutput(BaseModel):
    model_config = ConfigDict(extra='ignore')

    streams: list[FfprobeStream] = []
    format: FfprobeFormat


class MediaInfo(BaseModel):
    model_config = ConfigDict(frozen=True)

    width: int
    height: int
    duration_s: float
    has_audio: bool
    comment: str | None


async def probe_media(path: Path) -> MediaInfo:
    raw = await run_tool(
        FFPROBE_BINARY,
        ['-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', str(path)],
    )
    output = FfprobeOutput.model_validate_json(raw)
    video = next((stream for stream in output.streams if stream.codec_type == VIDEO_CODEC_TYPE), None)
    tags = {key.lower(): value for key, value in output.format.tags.items()}
    return MediaInfo(
        width=video.width or 0 if video else 0,
        height=video.height or 0 if video else 0,
        duration_s=output.format.duration,
        has_audio=any(stream.codec_type == AUDIO_CODEC_TYPE for stream in output.streams),
        comment=tags.get(COMMENT_TAG),
    )
