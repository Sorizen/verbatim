from pydantic import BaseModel

from app.enums import RunStatus
from app.exceptions import PipelineError
from app.pipeline.contracts import (
    Brief,
    Cast,
    Contract,
    Critique,
    Portrait,
    PortraitCheck,
    RenderAttempt,
    Scene,
    SceneCheck,
    Script,
    ShotFix,
)

MISSING_TEMPLATE = 'pipeline state has no {field} yet'


class RunOutcome(Contract):
    status: RunStatus
    final_video: str | None
    best_attempt: int | None
    review_reason: str | None


class PipelineState(BaseModel):
    run_id: str
    idea: str
    brief: Brief | None = None
    script: Script | None = None
    script_revision: int = 0
    critique: Critique | None = None
    cast: Cast | None = None
    portraits: dict[str, Portrait] = {}
    portrait_round: int = 0
    portrait_checks: list[PortraitCheck] = []
    scene: Scene | None = None
    attempt: int = 0
    attempts: list[RenderAttempt] = []
    scene_checks: list[SceneCheck] = []
    shot_fix: ShotFix | None = None
    review_approved: bool | None = None
    outcome: RunOutcome | None = None

    def require_brief(self) -> Brief:
        if not self.brief:
            raise PipelineError(MISSING_TEMPLATE.format(field='brief'))
        return self.brief

    def require_script(self) -> Script:
        if not self.script:
            raise PipelineError(MISSING_TEMPLATE.format(field='script'))
        return self.script

    def require_cast(self) -> Cast:
        if not self.cast:
            raise PipelineError(MISSING_TEMPLATE.format(field='cast'))
        return self.cast

    def require_scene(self) -> Scene:
        if not self.scene:
            raise PipelineError(MISSING_TEMPLATE.format(field='scene'))
        return self.scene

    def require_last_check(self) -> SceneCheck:
        if not self.scene_checks:
            raise PipelineError(MISSING_TEMPLATE.format(field='scene check'))
        return self.scene_checks[-1]

    def require_outcome(self) -> RunOutcome:
        if not self.outcome:
            raise PipelineError(MISSING_TEMPLATE.format(field='outcome'))
        return self.outcome
