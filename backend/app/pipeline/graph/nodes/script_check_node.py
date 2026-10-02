from typing import Any

from langgraph.runtime import Runtime

from app.constants import CRITIQUE_FILE_TEMPLATE
from app.enums import ScriptVerdict, StepName
from app.pipeline.checks import decide_script_verdict
from app.pipeline.contracts import Critique, CritiqueDraft
from app.pipeline.graph.context import PipelineContext
from app.pipeline.graph.state import PipelineState
from app.pipeline.rules import check_script_rules

SCORES_TEMPLATE = 'hook {hook}, escalation {escalation}, ending {ending}'
VIOLATIONS_TEMPLATE = '{count} rule violations, first: {first}'
LINES_FROZEN_NOTE = 'passed: the text of every line is frozen from here on'


def describe_critique(critique: Critique) -> str:
    if critique.rule_violations:
        return VIOLATIONS_TEMPLATE.format(count=len(critique.rule_violations), first=critique.rule_violations[0].detail)
    if critique.review:
        return describe_scores(critique.review)
    return ''


def describe_scores(review: CritiqueDraft) -> str:
    return SCORES_TEMPLATE.format(
        hook=review.hook.score, escalation=review.escalation.score, ending=review.ending.score
    )


async def script_check_node(state: PipelineState, runtime: Runtime[PipelineContext]) -> dict[str, Any]:
    context = runtime.context
    brief = state.require_brief()
    script = state.require_script()
    async with context.reporter.step(StepName.SCRIPT_CHECK, state.script_revision) as step:
        violations = check_script_rules(script, brief)
        review = None
        if not violations:
            result = await context.crew.critic.review(brief=brief, script=script)
            step.add_cost(result.cost_usd)
            review = result.value
        critique = Critique(
            revision=state.script_revision,
            verdict=decide_script_verdict(violations, review),
            rule_violations=violations,
            review=review,
        )
        context.workspace.write_json(CRITIQUE_FILE_TEMPLATE.format(revision=state.script_revision), critique)
        if critique.verdict == ScriptVerdict.REVISE:
            step.reject(describe_critique(critique))
        else:
            step.note(LINES_FROZEN_NOTE)
    return {'critique': critique}
