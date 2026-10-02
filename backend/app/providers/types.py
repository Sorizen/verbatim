from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.enums import VideoJobStatus, VideoResolution


class ProviderModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class TextPart(ProviderModel):
    kind: Literal['text'] = 'text'
    text: str


class ImagePart(ProviderModel):
    kind: Literal['image'] = 'image'
    data_url: str


class AudioPart(ProviderModel):
    kind: Literal['audio'] = 'audio'
    data_base64: str
    audio_format: str


type ContentPart = TextPart | ImagePart | AudioPart


class ChatMessage(ProviderModel):
    role: Literal['system', 'user', 'assistant']
    parts: list[ContentPart]


class StructuredReply(ProviderModel):
    content: str
    cost_usd: float


class GeneratedImage(ProviderModel):
    data: bytes
    cost_usd: float


class VideoRequest(ProviderModel):
    model: str
    prompt: str
    duration_s: int
    resolution: VideoResolution
    aspect_ratio: str
    generate_audio: bool
    seed: int
    reference_images: list[str]


class VideoJob(ProviderModel):
    job_id: str
    status: VideoJobStatus
    cost_usd: float | None = None
    error: str | None = None


class TranscriptWord(ProviderModel):
    word: str
    start: float
    end: float


class TranscriptSegment(ProviderModel):
    text: str
    start: float
    end: float


class Transcript(ProviderModel):
    text: str
    words: list[TranscriptWord]
    segments: list[TranscriptSegment] = []
    cost_usd: float
