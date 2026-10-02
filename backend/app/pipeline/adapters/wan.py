import re

from app.constants import SECONDS_IN_MINUTE, VIDEO_ASPECT_RATIO, VIDEO_MODEL
from app.enums import AmbientLevel, CameraAngle, CameraMovement, ShotSize
from app.pipeline.contracts import Camera, Scene, SceneCharacter, SceneShot
from app.providers.types import VideoRequest

SHOT_SIZE_TEXT = {
    ShotSize.CLOSE_UP: 'Close-up',
    ShotSize.MEDIUM: 'Medium shot',
    ShotSize.WIDE: 'Wide shot',
}
MOVEMENT_TEXT = {
    CameraMovement.STATIC: 'static camera',
    CameraMovement.PUSH_IN: 'slow push-in',
    CameraMovement.PAN: 'slow pan',
    CameraMovement.HANDHELD: 'handheld',
}
ANGLE_TEXT = {
    CameraAngle.EYE_LEVEL: 'eye level',
    CameraAngle.LOW: 'low angle',
    CameraAngle.HIGH: 'high angle',
    CameraAngle.OVER_SHOULDER: 'over the shoulder',
}
AMBIENT_TEMPLATES = {
    AmbientLevel.NORMAL: 'Background sound: {ambient}, quieter than speech.',
    AmbientLevel.LOW: 'Background sound, kept very quiet: {ambient}.',
    AmbientLevel.NONE: 'No background sound or music during dialogue.',
}
CHARACTER_ID_PATTERN = re.compile(r'\bc[1-3]\b')
OVERVIEW_TEMPLATE = '{place}, {time_of_day}. Vertical 9:16 live-action scene, {duration} seconds, {count} shots.'
SUBJECT_TEMPLATE = 'Subject locking: {subjects}.'
SUBJECT_ITEM_TEMPLATE = '{name} is Image {number}, {look}, wearing {wardrobe}'
SHOT_TEMPLATE = 'Shot {number} ({start}-{end}): {camera}. {action}'
DIALOGUE_TEMPLATE = '{name} says in a {voice}, {delivery}: "{text}"'
NO_DIALOGUE = 'No dialogue.'
SOUND_TEMPLATE = 'Sound: {sfx}.'
STYLE_TEMPLATE = 'Style and mood: {style}.'
NEGATIVE_TEMPLATE = 'Negative prompt list: {items}.'
SPEECH_RULE = 'Only the named characters speak, each quoted line exactly once and word for word.'
TIMESTAMP_TEMPLATE = '{minutes:02d}:{seconds:02d}'
LIST_SEPARATOR = ', '
SUBJECT_SEPARATOR = '; '
LINE_SEPARATOR = '\n'


def format_timestamp(total_seconds: int) -> str:
    minutes, seconds = divmod(total_seconds, SECONDS_IN_MINUTE)
    return TIMESTAMP_TEMPLATE.format(minutes=minutes, seconds=seconds)


def describe_camera(camera: Camera) -> str:
    return f'{SHOT_SIZE_TEXT[camera.size]}, {MOVEMENT_TEXT[camera.movement]}, {ANGLE_TEXT[camera.angle]}'


def name_characters(text: str, names: dict[str, str]) -> str:
    return CHARACTER_ID_PATTERN.sub(lambda match: names.get(match.group(0), match.group(0)), text)


def describe_subjects(characters: list[SceneCharacter]) -> str:
    subjects = [
        SUBJECT_ITEM_TEMPLATE.format(
            name=character.name, number=number, look=character.look, wardrobe=character.wardrobe
        )
        for number, character in enumerate(characters, start=1)
    ]
    return SUBJECT_TEMPLATE.format(subjects=SUBJECT_SEPARATOR.join(subjects))


def describe_shot(number: int, start: int, shot: SceneShot, characters: dict[str, SceneCharacter]) -> list[str]:
    names = {character_id: character.name for character_id, character in characters.items()}
    header = SHOT_TEMPLATE.format(
        number=number,
        start=format_timestamp(start),
        end=format_timestamp(start + shot.duration_s),
        camera=describe_camera(shot.camera),
        action=name_characters(shot.action, names),
    )
    lines = [header]
    if shot.dialogue:
        speaker = characters[shot.dialogue.speaker]
        lines.append(
            DIALOGUE_TEMPLATE.format(
                name=speaker.name, voice=speaker.voice, delivery=shot.dialogue.delivery, text=shot.dialogue.text
            )
        )
    else:
        lines.append(NO_DIALOGUE)
    if shot.sfx:
        lines.append(SOUND_TEMPLATE.format(sfx=LIST_SEPARATOR.join(shot.sfx)))
    return lines


def render_wan_prompt(scene: Scene) -> str:
    characters = {character.id: character for character in scene.characters}
    lines = [
        OVERVIEW_TEMPLATE.format(
            place=scene.setting.place,
            time_of_day=scene.setting.time_of_day.value,
            duration=scene.format.duration_s,
            count=len(scene.shots),
        ),
        describe_subjects(scene.characters),
    ]
    start = 0
    for number, shot in enumerate(scene.shots, start=1):
        lines.extend(describe_shot(number, start, shot, characters))
        start += shot.duration_s
    lines.extend(
        [
            AMBIENT_TEMPLATES[scene.setting.ambient_level].format(ambient=scene.setting.ambient_sound),
            STYLE_TEMPLATE.format(style=scene.style),
            SPEECH_RULE,
            NEGATIVE_TEMPLATE.format(items=LIST_SEPARATOR.join(scene.negative)),
        ]
    )
    return LINE_SEPARATOR.join(lines)


def build_wan_request(scene: Scene, *, reference_images: list[str], seed: int) -> VideoRequest:
    return VideoRequest(
        model=VIDEO_MODEL,
        prompt=render_wan_prompt(scene),
        duration_s=scene.format.duration_s,
        resolution=scene.format.resolution,
        aspect_ratio=VIDEO_ASPECT_RATIO,
        generate_audio=True,
        seed=seed,
        reference_images=reference_images,
    )
