from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from app.providers.types import ChatMessage, GeneratedImage, StructuredReply, Transcript, VideoJob, VideoRequest


class LlmClient(Protocol):
    async def complete(
        self,
        *,
        model: str,
        messages: list[ChatMessage],
        schema_name: str,
        json_schema: dict[str, Any],
    ) -> StructuredReply: ...


class ImageClient(Protocol):
    async def generate(self, *, model: str, prompt: str, aspect_ratio: str) -> GeneratedImage: ...


class VideoClient(Protocol):
    async def submit(self, request: VideoRequest) -> VideoJob: ...

    async def poll(self, job_id: str) -> VideoJob: ...

    async def download(self, job_id: str, destination: Path) -> None: ...


class SpeechClient(Protocol):
    async def transcribe(self, *, model: str, audio_path: Path) -> Transcript: ...


@dataclass(frozen=True)
class Providers:
    llm: LlmClient
    images: ImageClient
    videos: VideoClient
    speech: SpeechClient
