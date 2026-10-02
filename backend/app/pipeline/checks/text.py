import re

APOSTROPHE_TRANSLATION = str.maketrans({'’': "'", '‘': "'", 'ʼ': "'"})
TOKEN_SPLIT_PATTERN = re.compile(r"[^a-z0-9']+")
APOSTROPHE = "'"
DIGITS_PATTERN = re.compile(r'^\d+$')
MAX_SPELLED_NUMBER = 999
HUNDRED = 100
TEN = 10
UNITS = (
    'zero',
    'one',
    'two',
    'three',
    'four',
    'five',
    'six',
    'seven',
    'eight',
    'nine',
    'ten',
    'eleven',
    'twelve',
    'thirteen',
    'fourteen',
    'fifteen',
    'sixteen',
    'seventeen',
    'eighteen',
    'nineteen',
)
TENS = ('', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety')
TEENS_LIMIT = 20
HUNDRED_WORD = 'hundred'


def spell_number(number: int) -> list[str]:
    if number < TEENS_LIMIT:
        return [UNITS[number]]
    if number < HUNDRED:
        tens, units = divmod(number, TEN)
        return [TENS[tens]] if not units else [TENS[tens], UNITS[units]]
    hundreds, rest = divmod(number, HUNDRED)
    words = [UNITS[hundreds], HUNDRED_WORD]
    return words if not rest else [*words, *spell_number(rest)]


def expand_token(token: str) -> list[str]:
    if not DIGITS_PATTERN.match(token) or int(token) > MAX_SPELLED_NUMBER:
        return [token]
    return spell_number(int(token))


def normalize_words(text: str) -> list[str]:
    lowered = text.lower().translate(APOSTROPHE_TRANSLATION)
    tokens = [token.strip(APOSTROPHE) for token in TOKEN_SPLIT_PATTERN.split(lowered)]
    return [word for token in tokens if token for word in expand_token(token)]


def count_words(text: str) -> int:
    return len(normalize_words(text))
