import base64
from pathlib import Path

import anyio

from app.constants import (
    SPEECH_AUDIO_FORMAT,
    SPEECH_LANGUAGE,
    SPEECH_RESPONSE_FORMAT,
    SPEECH_TIMESTAMP_GRANULARITIES,
    TRANSCRIPTIONS_PATH,
)
from app.providers.openrouter.http import OpenRouterHttp
from app.providers.openrouter.schemas import SpeechTranscription, cost_of
from app.providers.types import Transcript, TranscriptSegment, TranscriptWord


class OpenRouterSpeech:
    def __init__(self, http: OpenRouterHttp) -> None:
        self._http = http

    async def transcribe(self, *, model: str, audio_path: Path) -> Transcript:
        audio = await anyio.Path(audio_path).read_bytes()
        body = {
            'model': model,
            'input_audio': {
                'data': base64.b64encode(audio).decode(),
                'format': SPEECH_AUDIO_FORMAT,
            },
            'language': SPEECH_LANGUAGE,
            'response_format': SPEECH_RESPONSE_FORMAT,
            'timestamp_granularities': list(SPEECH_TIMESTAMP_GRANULARITIES),
        }
        transcription = SpeechTranscription.model_validate(await self._http.post_json(TRANSCRIPTIONS_PATH, body))
        return Transcript(
            text=transcription.text,
            words=[TranscriptWord(word=word.word, start=word.start, end=word.end) for word in transcription.words],
            segments=[
                TranscriptSegment(text=segment.text, start=segment.start, end=segment.end)
                for segment in transcription.segments
            ],
            cost_usd=cost_of(transcription.usage),
        )
