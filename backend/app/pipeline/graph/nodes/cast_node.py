from typing import Any

from langgraph.runtime import Runtime

from app.constants import CAST_FILE
from app.enums import StepName
from app.pipeline.graph.context import PipelineContext
from app.pipeline.graph.state import PipelineState

CAST_NOTE_SEPARATOR = ', '


async def cast_node(state: PipelineState, runtime: Runtime[PipelineContext]) -> dict[str, Any]:
    context = runtime.context
    async with context.reporter.step(StepName.CAST) as step:
        result = await context.crew.casting.cast(brief=state.require_brief(), script=state.require_script())
        step.add_cost(result.cost_usd)
        context.workspace.write_json(CAST_FILE, result.value)
        step.note(CAST_NOTE_SEPARATOR.join(member.voice for member in result.value.characters))
    return {'cast': result.value, 'portraits': {}, 'portrait_round': 0, 'portrait_checks': []}
