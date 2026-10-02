import asyncio
from typing import Any

from langgraph.runtime import Runtime

from app.constants import PORTRAITS_CHECK_FILE_TEMPLATE
from app.enums import PortraitVerdict, StepName
from app.pipeline.checks import decide_portrait_verdict
from app.pipeline.contracts import CastMember, Portrait, PortraitCheck, PortraitsCheck
from app.pipeline.graph.context import PipelineContext
from app.pipeline.graph.state import PipelineState

REDRAW_TEMPLATE = 'redraw: {ids}'
IDS_SEPARATOR = ', '


async def review_portrait(
    context: PipelineContext,
    member: CastMember,
    portrait: Portrait,
) -> tuple[PortraitCheck, float]:
    result = await context.crew.portrait_judge.review(
        member=member, portrait_path=context.workspace.resolve(portrait.path)
    )
    check = PortraitCheck(
        character_id=member.id,
        attempt=portrait.attempt,
        portrait_path=portrait.path,
        review=result.value,
        verdict=decide_portrait_verdict(result.value.scores),
    )
    return check, result.cost_usd


async def portrait_check_node(state: PipelineState, runtime: Runtime[PipelineContext]) -> dict[str, Any]:
    context = runtime.context
    cast = state.require_cast()
    fresh = [portrait for portrait in state.portraits.values() if portrait.attempt == state.portrait_round]
    async with context.reporter.step(StepName.PORTRAIT_CHECK, state.portrait_round) as step:
        reviewed = await asyncio.gather(
            *(review_portrait(context, cast.member(portrait.character_id), portrait) for portrait in fresh)
        )
        step.add_cost(sum(cost for _, cost in reviewed))
        latest = {check.character_id: check for check in state.portrait_checks}
        latest.update({check.character_id: check for check, _ in reviewed})
        checks = list(latest.values())
        context.workspace.write_json(
            PORTRAITS_CHECK_FILE_TEMPLATE.format(round=state.portrait_round),
            PortraitsCheck(round=state.portrait_round, checks=checks),
        )
        rejected = [check.character_id for check, _ in reviewed if check.verdict == PortraitVerdict.REDRAW]
        if rejected:
            step.reject(REDRAW_TEMPLATE.format(ids=IDS_SEPARATOR.join(rejected)))
    return {'portrait_checks': checks}
