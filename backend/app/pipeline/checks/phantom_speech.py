import re

from app.enums import PhantomSpeech
from app.pipeline.checks.text import normalize_words
from app.pipeline.contracts import IgnoredSpeech
from app.providers.types import Transcript, TranscriptSegment, TranscriptWord

SOUND_NOTE = re.compile(r'^\W*[*\[(\u266a].*[*\])\u266a]\W*$')
KNOWN_PHRASES = frozenset(
    {
        ('thank', 'you'),
        ('thank', 'you', 'very', 'much'),
        ('thanks', 'for', 'watching'),
        ('thank', 'you', 'for', 'watching'),
        ('please', 'subscribe'),
    }
)


def contains_run(words: list[str], run: tuple[str, ...]) -> bool:
    size = len(run)
    return any(tuple(words[index : index + size]) == run for index in range(len(words) - size + 1))


def classify_segment(segment: TranscriptSegment, expected_words: list[str]) -> PhantomSpeech | None:
    if SOUND_NOTE.match(segment.text):
        return PhantomSpeech.SOUND_NOTE
    words = tuple(normalize_words(segment.text))
    if words in KNOWN_PHRASES and not contains_run(expected_words, words):
        return PhantomSpeech.KNOWN_PHRASE
    return None


def find_phantom_speech(segments: list[TranscriptSegment], expected_words: list[str]) -> list[IgnoredSpeech]:
    found: list[IgnoredSpeech] = []
    for segment in segments:
        reason = classify_segment(segment, expected_words)
        if reason:
            found.append(
                IgnoredSpeech(text=segment.text.strip(), start_s=segment.start, end_s=segment.end, reason=reason)
            )
    return found


def is_inside(word: TranscriptWord, ignored: list[IgnoredSpeech]) -> bool:
    middle = (word.start + word.end) / 2
    return any(item.start_s <= middle <= item.end_s for item in ignored)


def drop_phantom_speech(transcript: Transcript, expected_words: list[str]) -> tuple[Transcript, list[IgnoredSpeech]]:
    ignored = find_phantom_speech(transcript.segments, expected_words)
    if not ignored:
        return transcript, ignored
    words = [word for word in transcript.words if not is_inside(word, ignored)]
    return transcript.model_copy(update={'words': words}), ignored
