from app.exceptions import ContractViolationError
from app.pipeline.contracts import Scene, Script

SHOT_IDS_CHANGED = 'scene shots {scene_ids} differ from script shots {script_ids}'
DIALOGUE_PRESENCE_CHANGED = 'shot {shot_id}: dialogue presence differs from the script'
LINE_CHANGED = 'shot {shot_id}: the line differs from script.json, lines are frozen after the script check'


def verify_lines_unchanged(scene: Scene, script: Script) -> None:
    scene_ids = [shot.id for shot in scene.shots]
    script_ids = [shot.id for shot in script.shots]
    if scene_ids != script_ids:
        raise ContractViolationError(SHOT_IDS_CHANGED.format(scene_ids=scene_ids, script_ids=script_ids))
    for scene_shot, script_shot in zip(scene.shots, script.shots, strict=True):
        if bool(scene_shot.dialogue) != bool(script_shot.line):
            raise ContractViolationError(DIALOGUE_PRESENCE_CHANGED.format(shot_id=scene_shot.id))
        if not scene_shot.dialogue or not script_shot.line:
            continue
        same_text = scene_shot.dialogue.text == script_shot.line.text
        same_speaker = scene_shot.dialogue.speaker == script_shot.line.speaker
        if not same_text or not same_speaker:
            raise ContractViolationError(LINE_CHANGED.format(shot_id=scene_shot.id))
