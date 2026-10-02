from collections.abc import Iterable

QUOTE_CHARACTERS = ('"', '“', '”', '«', '»')
QUOTE_ERROR = 'free-text fields must not contain quotation marks: dialogue is inserted by code'


def ensure_no_quotes(texts: Iterable[str | None]) -> None:
    for text in texts:
        if text and any(quote in text for quote in QUOTE_CHARACTERS):
            raise ValueError(QUOTE_ERROR)
