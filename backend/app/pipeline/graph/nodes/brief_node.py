from typing import Any

from langgraph.runtime import Runtime

from app.constants import BRIEF_FILE
from app.enums import StepName
from app.pipeline.contracts import Brief
from app.pipeline.graph.context import PipelineContext
from app.pipeline.graph.state import PipelineState
from app.pipeline.rules import ensure_locked_lines_fit, extract_locked_lines


async def brief_node(state: PipelineState, runtime: Runtime[PipelineContext]) -> dict[str, Any]:
    context = runtime.context
    async with context.reporter.step(StepName.BRIEF) as step:
        locked_lines = extract_locked_lines(state.idea)
        ensure_locked_lines_fit(locked_lines)
        result = await context.crew.producer.write_brief(idea=state.idea, locked_lines=locked_lines)
        step.add_cost(result.cost_usd)
        brief = Brief.model_validate({**result.value.model_dump(), 'locked_lines': locked_lines})
        context.workspace.write_json(BRIEF_FILE, brief)
        step.note(brief.logline)
    return {'brief': brief}
