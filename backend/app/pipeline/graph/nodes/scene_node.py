from typing import Any

from langgraph.runtime import Runtime

from app.constants import SCENE_FILE
from app.enums import StepName
from app.pipeline.graph.context import PipelineContext
from app.pipeline.graph.state import PipelineState
from app.pipeline.rules import assemble_scene

SCENE_NOTE_TEMPLATE = '{count} shots, {seconds} s, {resolution}'


async def scene_node(state: PipelineState, runtime: Runtime[PipelineContext]) -> dict[str, Any]:
    context = runtime.context
    brief = state.require_brief()
    script = state.require_script()
    cast = state.require_cast()
    async with context.reporter.step(StepName.SCENE) as step:
        result = await context.crew.director.stage(brief=brief, script=script, cast=cast)
        step.add_cost(result.cost_usd)
        scene = assemble_scene(
            draft=result.value,
            brief=brief,
            script=script,
            cast=cast,
            portraits={character_id: portrait.path for character_id, portrait in state.portraits.items()},
            resolution=context.resolution,
        )
        context.workspace.write_json(SCENE_FILE, scene)
        step.note(
            SCENE_NOTE_TEMPLATE.format(
                count=len(scene.shots), seconds=scene.format.duration_s, resolution=scene.format.resolution.value
            )
        )
    return {'scene': scene}
