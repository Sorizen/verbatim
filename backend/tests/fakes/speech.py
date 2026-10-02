from pathlib import Path

from app.media import probe_media
from app.providers.types import Transcript, TranscriptWord
from tests.fakes.spoken import SPOKEN_LINES_ADAPTER, SpokenLine

EMPTY_JSON_LIST = '[]'
WORD_SEPARATOR = ' '


def spread_words(line: SpokenLine) -> list[TranscriptWord]:
    tokens = line.text.split()
    if not tokens:
        return []
    span = (line.end - line.start) / len(tokens)
    return [
        TranscriptWord(word=token, start=line.start + index * span, end=line.start + (index + 1) * span)
        for index, token in enumerate(tokens)
    ]


class FakeSpeech:
    async def transcribe(self, *, model: str, audio_path: Path) -> Transcript:
        info = await probe_media(audio_path)
        lines = SPOKEN_LINES_ADAPTER.validate_json(info.comment or EMPTY_JSON_LIST)
        words = [word for line in lines for word in spread_words(line)]
        return Transcript(text=WORD_SEPARATOR.join(word.word for word in words), words=words, cost_usd=0.0)
