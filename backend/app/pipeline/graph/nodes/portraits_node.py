import asyncio
from typing import Any

from langgraph.runtime import Runtime

from app.constants import IMAGE_MODEL, PORTRAIT_ASPECT_RATIO, PORTRAIT_FILE_TEMPLATE
from app.enums import PortraitVerdict, StepName
from app.media import ensure_jpeg
from app.pipeline.contracts import Cast, CastMember, Portrait, PortraitCheck
from app.pipeline.graph.context import PipelineContext
from app.pipeline.graph.state import PipelineState

DRAWN_TEMPLATE = 'drawn: {ids}'
IDS_SEPARATOR = ', '
FIRST_ROUND = 1


def members_to_draw(cast: Cast, checks: list[PortraitCheck], round_number: int) -> list[CastMember]:
    if round_number == FIRST_ROUND:
        return cast.characters
    rejected = {check.character_id for check in checks if check.verdict == PortraitVerdict.REDRAW}
    return [member for member in cast.characters if member.id in rejected]


async def draw_portrait(context: PipelineContext, member: CastMember, round_number: int) -> tuple[Portrait, float]:
    image = await context.providers.images.generate(
        model=IMAGE_MODEL, prompt=member.portrait_prompt, aspect_ratio=PORTRAIT_ASPECT_RATIO
    )
    relative = PORTRAIT_FILE_TEMPLATE.format(character_id=member.id, round=round_number)
    await ensure_jpeg(context.workspace.write_bytes(relative, image.data))
    return Portrait(character_id=member.id, path=relative, attempt=round_number), image.cost_usd


async def portraits_node(state: PipelineState, runtime: Runtime[PipelineContext]) -> dict[str, Any]:
    context = runtime.context
    round_number = state.portrait_round + 1
    members = members_to_draw(state.require_cast(), state.portrait_checks, round_number)
    async with context.reporter.step(StepName.PORTRAITS, round_number) as step:
        drawn = await asyncio.gather(*(draw_portrait(context, member, round_number) for member in members))
        step.add_cost(sum(cost for _, cost in drawn))
        step.note(DRAWN_TEMPLATE.format(ids=IDS_SEPARATOR.join(portrait.character_id for portrait, _ in drawn)))
    portraits = {**state.portraits, **{portrait.character_id: portrait for portrait, _ in drawn}}
    return {'portraits': portraits, 'portrait_round': round_number}
