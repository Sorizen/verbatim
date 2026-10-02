from app.enums import DiffOp
from app.pipeline.checks import align_words, count_errors, normalize_words

SCRIPT_LINE = 'Nice hat, big man. Did your mother pick it out?'
HEARD_LINE = 'Nice hat, big guy. Your mother picked it out?'


def test_normalize_ignores_case_punctuation_and_curly_apostrophes() -> None:
    assert normalize_words('Say THAT again, and you’ll be... picking up your teeth!') == [
        'say',
        'that',
        'again',
        'and',
        "you'll",
        'be',
        'picking',
        'up',
        'your',
        'teeth',
    ]


def test_normalize_spells_digits_as_words() -> None:
    assert normalize_words('I owe you 25 dollars') == ['i', 'owe', 'you', 'twenty', 'five', 'dollars']


def test_alignment_counts_substitutions_and_deletions() -> None:
    pairs = align_words(normalize_words(SCRIPT_LINE), normalize_words(HEARD_LINE))
    errors = [pair.op for pair in pairs if pair.op]
    assert count_errors(pairs) == 3
    assert errors.count(DiffOp.SUBSTITUTE) == 2
    assert errors.count(DiffOp.DELETE) == 1


def test_alignment_of_identical_lines_has_no_errors() -> None:
    words = normalize_words(SCRIPT_LINE)
    assert count_errors(align_words(words, list(words))) == 0
