from typing import Any

from langgraph.types import interrupt

from app.enums import PortraitVerdict, RunStatus, StepName
from app.pipeline.graph.nodes.script_check_node import describe_critique
from app.pipeline.graph.state import PipelineState, RunOutcome

SCRIPT_REVIEW_REASON = 'the script did not pass its check after every rewrite: {details}'
PORTRAIT_REVIEW_REASON = 'portraits {ids} did not pass their check after every redraw'
REJECTED_REASON = 'rejected by the reviewer'
IDS_SEPARATOR = ', '


def review_payload(step: StepName, reason: str) -> dict[str, str]:
    return {'step': step.value, 'reason': reason}


async def script_review_node(state: PipelineState) -> dict[str, Any]:
    details = describe_critique(state.critique) if state.critique else ''
    approved = interrupt(review_payload(StepName.SCRIPT_CHECK, SCRIPT_REVIEW_REASON.format(details=details)))
    return {'review_approved': bool(approved)}


async def portrait_review_node(state: PipelineState) -> dict[str, Any]:
    rejected = [check.character_id for check in state.portrait_checks if check.verdict == PortraitVerdict.REDRAW]
    reason = PORTRAIT_REVIEW_REASON.format(ids=IDS_SEPARATOR.join(rejected))
    approved = interrupt(review_payload(StepName.PORTRAIT_CHECK, reason))
    return {'review_approved': bool(approved)}


async def take_review_node(state: PipelineState) -> dict[str, Any]:
    outcome = state.require_outcome()
    approved = interrupt(review_payload(StepName.SCENE_CHECK, outcome.review_reason or ''))
    if approved:
        return {'review_approved': True, 'outcome': outcome.model_copy(update={'status': RunStatus.DONE})}
    rejected = outcome.model_copy(update={'status': RunStatus.FAILED, 'review_reason': REJECTED_REASON})
    return {'review_approved': False, 'outcome': rejected}


async def rejected_node(_: PipelineState) -> dict[str, Any]:
    outcome = RunOutcome(status=RunStatus.FAILED, final_video=None, best_attempt=None, review_reason=REJECTED_REASON)
    return {'outcome': outcome}
