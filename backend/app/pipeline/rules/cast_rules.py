from app.exceptions import ContractViolationError
from app.pipeline.contracts import Brief, Cast

CAST_MISMATCH = 'the cast must describe characters {expected} in this order, got {received}'


def check_cast_matches_brief(cast: Cast, brief: Brief) -> None:
    expected = [character.id for character in brief.characters]
    received = [member.id for member in cast.characters]
    if expected != received:
        raise ContractViolationError(CAST_MISMATCH.format(expected=expected, received=received))
