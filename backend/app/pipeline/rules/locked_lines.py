import re

from app.constants import MAX_SHOT_SECONDS, MAX_WORDS_PER_SECOND
from app.exceptions import LockedLineTooLongError
from app.pipeline.checks.text import count_words

QUOTED_SPEECH_PATTERN = re.compile(r'"([^"]+)"|“([^”]+)”')
TOO_LONG_TEMPLATE = (
    'The quoted line "{line}" has {words} words and does not fit one {seconds}-second shot. '
    'It cannot be shortened automatically: please split it or make it shorter in the idea.'
)


def extract_locked_lines(idea: str) -> list[str]:
    lines = []
    for straight, curly in QUOTED_SPEECH_PATTERN.findall(idea):
        line = (straight or curly).strip()
        if line:
            lines.append(line)
    return lines


def ensure_locked_lines_fit(lines: list[str]) -> None:
    max_words = int(MAX_SHOT_SECONDS * MAX_WORDS_PER_SECOND)
    for line in lines:
        words = count_words(line)
        if words > max_words:
            raise LockedLineTooLongError(TOO_LONG_TEMPLATE.format(line=line, words=words, seconds=MAX_SHOT_SECONDS))
