from pydantic import Field

from app.constants import CRITIC_MAX_SCORE, CRITIC_MIN_SCORE
from app.enums import ScriptIssueKind, ScriptVerdict
from app.pipeline.contracts.base import Contract


class CriticScore(Contract):
    score: int = Field(ge=CRITIC_MIN_SCORE, le=CRITIC_MAX_SCORE)
    reason: str
    improvements: list[str]


class CritiqueDraft(Contract):
    hook: CriticScore = Field(description='Opening attraction of the first shot only')
    escalation: CriticScore = Field(description='How the conflict rises from line to line')
    ending: CriticScore = Field(description='Ending hook of the last shot only')


class RuleViolation(Contract):
    kind: ScriptIssueKind
    shot_id: str | None
    detail: str


class Critique(Contract):
    revision: int
    verdict: ScriptVerdict
    rule_violations: list[RuleViolation]
    review: CritiqueDraft | None
