from typing import Any

from langgraph.runtime import Runtime

from app.constants import SCENE_FILE, SHOT_FIX_FILE
from app.enums import StepName
from app.exceptions import PipelineError
from app.pipeline.checks import first_failed_line
from app.pipeline.graph.context import PipelineContext
from app.pipeline.graph.state import PipelineState
from app.pipeline.rules import apply_shot_fix

NO_FAILED_LINE = 'the scene check has no failed line to rebuild'
FIX_NOTE_TEMPLATE = '{shot_id}: {reason}, {seconds} s, words unchanged'


async def shot_fix_node(state: PipelineState, runtime: Runtime[PipelineContext]) -> dict[str, Any]:
    context = runtime.context
    scene = state.require_scene()
    check = state.require_last_check()
    failed = first_failed_line(check.lines)
    if not failed:
        raise PipelineError(NO_FAILED_LINE)
    async with context.reporter.step(StepName.SHOT_FIX, state.attempt) as step:
        result = await context.crew.shot_fixer.rebuild(scene=scene, check=check, shot_id=failed.shot_id)
        step.add_cost(result.cost_usd)
        rebuilt = apply_shot_fix(scene, result.value, state.require_script())
        context.workspace.write_json(SHOT_FIX_FILE, result.value)
        context.workspace.write_json(SCENE_FILE, rebuilt)
        step.note(
            FIX_NOTE_TEMPLATE.format(
                shot_id=failed.shot_id, reason=result.value.reason.value, seconds=result.value.duration_s
            )
        )
    return {'scene': rebuilt, 'shot_fix': result.value}
