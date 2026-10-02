from app.constants import VIDEO_ASPECT_RATIO
from app.enums import AmbientLevel, VideoResolution
from app.exceptions import ContractViolationError
from app.pipeline.contracts import (
    Brief,
    Cast,
    Dialogue,
    Scene,
    SceneCharacter,
    SceneDraft,
    SceneFormat,
    SceneSetting,
    SceneShot,
    SceneShotDraft,
    Script,
    Shot,
)
from app.pipeline.rules.line_integrity import verify_lines_unchanged

DRAFT_SHOTS_MISMATCH = 'the staging must cover shots {expected} in this order, got {received}'
DELIVERY_MISSING = 'shot {shot_id} has a line, so delivery is required'
DELIVERY_UNEXPECTED = 'shot {shot_id} has no line, so delivery must be null'


def check_draft_matches_script(draft: SceneDraft, script: Script) -> None:
    expected = [shot.id for shot in script.shots]
    received = [shot.id for shot in draft.shots]
    if expected != received:
        raise ContractViolationError(DRAFT_SHOTS_MISMATCH.format(expected=expected, received=received))
    for draft_shot, script_shot in zip(draft.shots, script.shots, strict=True):
        if script_shot.line and not draft_shot.delivery:
            raise ContractViolationError(DELIVERY_MISSING.format(shot_id=draft_shot.id))
        if not script_shot.line and draft_shot.delivery:
            raise ContractViolationError(DELIVERY_UNEXPECTED.format(shot_id=draft_shot.id))


def build_scene_shot(script_shot: Shot, draft_shot: SceneShotDraft) -> SceneShot:
    dialogue = None
    if script_shot.line:
        dialogue = Dialogue(
            speaker=script_shot.line.speaker,
            text=script_shot.line.text,
            delivery=draft_shot.delivery or '',
        )
    return SceneShot(
        id=script_shot.id,
        duration_s=script_shot.duration_s,
        camera=draft_shot.camera,
        action=draft_shot.action,
        dialogue=dialogue,
        sfx=draft_shot.sfx,
    )


def build_scene_characters(brief: Brief, cast: Cast, portraits: dict[str, str]) -> list[SceneCharacter]:
    names = {character.id: character.name for character in brief.characters}
    return [
        SceneCharacter(
            id=member.id,
            name=names[member.id],
            look=member.look,
            wardrobe=member.wardrobe,
            voice=member.voice,
            portrait=portraits[member.id],
        )
        for member in cast.characters
    ]


def assemble_scene(
    *,
    draft: SceneDraft,
    brief: Brief,
    script: Script,
    cast: Cast,
    portraits: dict[str, str],
    resolution: VideoResolution,
) -> Scene:
    check_draft_matches_script(draft, script)
    scene = Scene(
        format=SceneFormat(aspect=VIDEO_ASPECT_RATIO, resolution=resolution, duration_s=script.total_seconds),
        style=draft.style,
        characters=build_scene_characters(brief, cast, portraits),
        setting=SceneSetting(
            place=draft.setting.place,
            time_of_day=brief.setting.time_of_day,
            light=draft.setting.light,
            ambient_sound=draft.setting.ambient_sound,
            ambient_level=AmbientLevel.NORMAL,
        ),
        shots=[
            build_scene_shot(script_shot, draft_shot)
            for script_shot, draft_shot in zip(script.shots, draft.shots, strict=True)
        ],
        negative=draft.negative,
    )
    verify_lines_unchanged(scene, script)
    return scene
