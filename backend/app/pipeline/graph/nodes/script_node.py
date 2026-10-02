from typing import Any

from langgraph.runtime import Runtime

from app.constants import SCRIPT_FILE
from app.enums import StepName
from app.pipeline.graph.context import PipelineContext
from app.pipeline.graph.state import PipelineState
from app.pipeline.rules import assemble_script


async def script_node(state: PipelineState, runtime: Runtime[PipelineContext]) -> dict[str, Any]:
    context = runtime.context
    brief = state.require_brief()
    revision = state.script_revision + 1
    async with context.reporter.step(StepName.SCRIPT, revision) as step:
        result = await context.crew.screenwriter.write_script(brief=brief, feedback=state.critique)
        step.add_cost(result.cost_usd)
        script = assemble_script(result.value, brief.locked_lines)
        context.workspace.write_json(SCRIPT_FILE, script)
        step.note(script.title)
    return {'script': script, 'script_revision': revision}
