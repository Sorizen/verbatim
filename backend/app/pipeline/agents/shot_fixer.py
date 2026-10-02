from app.constants import LLM_MODEL
from app.enums import AgentRole
from app.pipeline.agents.caller import AgentResult, StructuredCaller
from app.pipeline.contracts import Scene, SceneCheck, ShotFix
from app.pipeline.rules import check_fix_fits_scene


class ShotFixer:
    def __init__(self, caller: StructuredCaller) -> None:
        self._caller = caller

    async def rebuild(self, *, scene: Scene, check: SceneCheck, shot_id: str) -> AgentResult[ShotFix]:
        return await self._caller.call(
            role=AgentRole.SHOT_FIXER,
            model=LLM_MODEL,
            schema=ShotFix,
            payload={
                'scene': scene.model_dump(mode='json'),
                'failed_shot_id': shot_id,
                'check': check.model_dump(mode='json'),
            },
            check=lambda fix: check_fix_fits_scene(fix, scene, shot_id),
        )
