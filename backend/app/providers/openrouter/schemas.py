from pydantic import BaseModel, ConfigDict

from app.enums import VideoJobStatus


class OpenRouterModel(BaseModel):
    model_config = ConfigDict(extra='ignore', frozen=True)


class Usage(OpenRouterModel):
    cost: float | None = None


class CompletionMessage(OpenRouterModel):
    content: str | None = None


class CompletionChoice(OpenRouterModel):
    message: CompletionMessage


class ChatCompletion(OpenRouterModel):
    choices: list[CompletionChoice]
    usage: Usage | None = None


class ImageDatum(OpenRouterModel):
    b64_json: str


class ImageGeneration(OpenRouterModel):
    data: list[ImageDatum]
    usage: Usage | None = None


class VideoJobResponse(OpenRouterModel):
    id: str
    status: VideoJobStatus
    usage: Usage | None = None
    error: str | None = None


class SpeechWord(OpenRouterModel):
    word: str
    start: float
    end: float


class SpeechSegment(OpenRouterModel):
    text: str
    start: float
    end: float


class SpeechTranscription(OpenRouterModel):
    text: str
    words: list[SpeechWord] = []
    segments: list[SpeechSegment] = []
    usage: Usage | None = None


def cost_of(usage: Usage | None) -> float:
    if not usage or usage.cost is None:
        return 0.0
    return usage.cost
