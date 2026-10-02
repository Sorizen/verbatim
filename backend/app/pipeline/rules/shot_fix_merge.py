from app.constants import MAX_SCENE_SECONDS, MIN_SCENE_SECONDS
from app.exceptions import ContractViolationError
from app.pipeline.contracts import Scene, SceneShot, Script, ShotFix
from app.pipeline.rules.line_integrity import verify_lines_unchanged

WRONG_SHOT = 'the fix targets shot {received}, but the failed shot is {expected}'
SCENE_TOO_LONG = 'after the fix the scene lasts {seconds} s, it must last {low}-{high} s'


def rebuild_shot(shot: SceneShot, fix: ShotFix) -> SceneShot:
    dialogue = shot.dialogue.model_copy(update={'delivery': fix.delivery}) if shot.dialogue else None
    return shot.model_copy(update={'duration_s': fix.duration_s, 'camera': fix.camera, 'dialogue': dialogue})


def check_fix_fits_scene(fix: ShotFix, scene: Scene, failed_shot_id: str) -> None:
    if fix.shot_id != failed_shot_id:
        raise ContractViolationError(WRONG_SHOT.format(received=fix.shot_id, expected=failed_shot_id))
    seconds = sum(fix.duration_s if shot.id == fix.shot_id else shot.duration_s for shot in scene.shots)
    if not MIN_SCENE_SECONDS <= seconds <= MAX_SCENE_SECONDS:
        raise ContractViolationError(
            SCENE_TOO_LONG.format(seconds=seconds, low=MIN_SCENE_SECONDS, high=MAX_SCENE_SECONDS)
        )


def apply_shot_fix(scene: Scene, fix: ShotFix, script: Script) -> Scene:
    shots = [rebuild_shot(shot, fix) if shot.id == fix.shot_id else shot for shot in scene.shots]
    updated = scene.model_copy(
        update={
            'shots': shots,
            'format': scene.format.model_copy(update={'duration_s': sum(shot.duration_s for shot in shots)}),
            'setting': scene.setting.model_copy(update={'ambient_level': fix.ambient_level}),
        }
    )
    verify_lines_unchanged(updated, script)
    return updated
