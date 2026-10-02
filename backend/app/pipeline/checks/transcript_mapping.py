from dataclasses import dataclass

from app.enums import DiffOp
from app.pipeline.checks.alignment import AlignedPair, align_words, count_errors
from app.pipeline.checks.text import normalize_words
from app.pipeline.contracts import AlignedWord, LineCheck, Script, WordDiff
from app.providers.types import Transcript

WORD_SEPARATOR = ' '


@dataclass(frozen=True)
class HeardToken:
    word: str
    start: float
    end: float


@dataclass(frozen=True)
class ExpectedLine:
    shot_id: str
    speaker: str
    text: str
    words: list[str]
    offset: int


def tokenize_transcript(transcript: Transcript) -> list[HeardToken]:
    return [
        HeardToken(word=word, start=item.start, end=item.end)
        for item in transcript.words
        for word in normalize_words(item.word)
    ]


def collect_expected_lines(script: Script) -> list[ExpectedLine]:
    lines: list[ExpectedLine] = []
    offset = 0
    for shot in script.shots:
        if not shot.line:
            continue
        words = normalize_words(shot.line.text)
        lines.append(ExpectedLine(shot.id, shot.line.speaker, shot.line.text, words, offset))
        offset += len(words)
    return lines


def owner_of(expected_index: int, lines: list[ExpectedLine]) -> int:
    return next(number for number, line in enumerate(lines) if expected_index < line.offset + len(line.words))


def group_pairs_by_line(pairs: list[AlignedPair], lines: list[ExpectedLine]) -> list[list[AlignedPair]]:
    groups: list[list[AlignedPair]] = [[] for _ in lines]
    current = 0
    for pair in pairs:
        if pair.expected_index is not None:
            current = owner_of(pair.expected_index, lines)
        groups[current].append(pair)
    return groups


def align_word(pair: AlignedPair, line: ExpectedLine, heard: list[HeardToken]) -> AlignedWord:
    expected = line.words[pair.expected_index - line.offset] if pair.expected_index is not None else None
    heard_word = heard[pair.heard_index].word if pair.heard_index is not None else None
    return AlignedWord(op=pair.op, expected=expected, heard=heard_word)


def to_word_diff(word: AlignedWord, op: DiffOp) -> WordDiff:
    return WordDiff(op=op, expected=word.expected, heard=word.heard)


def build_line_check(line: ExpectedLine, pairs: list[AlignedPair], heard: list[HeardToken]) -> LineCheck:
    heard_tokens = [heard[pair.heard_index] for pair in pairs if pair.heard_index is not None]
    alignment = [align_word(pair, line, heard) for pair in pairs]
    return LineCheck(
        shot_id=line.shot_id,
        speaker=line.speaker,
        expected=line.text,
        heard=WORD_SEPARATOR.join(token.word for token in heard_tokens),
        wer=count_errors(pairs) / max(len(line.words), 1),
        diff=[to_word_diff(word, op) for word in alignment if (op := word.op)],
        alignment=alignment,
        start_s=heard_tokens[0].start if heard_tokens else None,
        end_s=heard_tokens[-1].end if heard_tokens else None,
        speaker_matches=None,
    )


def expected_words(script: Script) -> list[str]:
    return [word for line in collect_expected_lines(script) for word in line.words]


def map_transcript_to_lines(script: Script, transcript: Transcript) -> list[LineCheck]:
    lines = collect_expected_lines(script)
    if not lines:
        return []
    heard = tokenize_transcript(transcript)
    expected_words = [word for line in lines for word in line.words]
    pairs = align_words(expected_words, [token.word for token in heard])
    groups = group_pairs_by_line(pairs, lines)
    return [build_line_check(line, group, heard) for line, group in zip(lines, groups, strict=True)]
