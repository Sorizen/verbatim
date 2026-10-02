import pytest

from app.enums import (
    AmbientLevel,
    CameraAngle,
    CameraMovement,
    ShotFixReason,
    ShotSize,
    TimeOfDay,
    VideoResolution,
)
from app.exceptions import ContractViolationError
from app.pipeline.adapters import render_wan_prompt
from app.pipeline.contracts import (
    Camera,
    Dialogue,
    Line,
    Scene,
    SceneCharacter,
    SceneFormat,
    SceneSetting,
    SceneShot,
    Script,
    Shot,
    ShotFix,
)
from app.pipeline.rules import apply_shot_fix, verify_lines_unchanged

LINE = "Say that again and you'll be picking up your teeth."
CAMERA = Camera(size=ShotSize.MEDIUM, movement=CameraMovement.STATIC, angle=CameraAngle.EYE_LEVEL)


def make_script() -> Script:
    return Script(
        title='The hat',
        shots=[
            Shot(id='s1', beat='reply', duration_s=5, line=Line(speaker='c2', text=LINE, emotion='x', locked=False)),
            Shot(id='s2', beat='fight', duration_s=5, line=None),
        ],
    )


def make_scene(text: str = LINE) -> Scene:
    return Scene(
        format=SceneFormat(aspect='9:16', resolution=VideoResolution.P480, duration_s=10),
        style='photoreal western',
        characters=[
            SceneCharacter(id='c1', name='Jake', look='lean', wardrobe='black coat', voice='dry voice', portrait='a'),
            SceneCharacter(id='c2', name='Tom', look='huge', wardrobe='vest', voice='deep voice', portrait='b'),
        ],
        setting=SceneSetting(
            place='saloon',
            time_of_day=TimeOfDay.NIGHT,
            light='oil lamps',
            ambient_sound='piano',
            ambient_level=AmbientLevel.NORMAL,
        ),
        shots=[
            SceneShot(
                id='s1',
                duration_s=5,
                camera=CAMERA,
                action='c2 turns to c1.',
                dialogue=Dialogue(speaker='c2', text=text, delivery='quiet'),
                sfx=['glass'],
            ),
            SceneShot(id='s2', duration_s=5, camera=CAMERA, action='c2 swings at c1.', dialogue=None, sfx=[]),
        ],
        negative=['subtitles'],
    )


def test_changed_line_is_rejected() -> None:
    with pytest.raises(ContractViolationError):
        verify_lines_unchanged(make_scene(text=LINE.replace('again', 'once more')), make_script())


def test_shot_fix_changes_staging_but_never_words() -> None:
    fix = ShotFix(
        shot_id='s1',
        duration_s=6,
        delivery='slower and louder',
        ambient_level=AmbientLevel.LOW,
        camera=Camera(size=ShotSize.CLOSE_UP, movement=CameraMovement.STATIC, angle=CameraAngle.EYE_LEVEL),
        reason=ShotFixReason.TRUNCATED,
    )
    rebuilt = apply_shot_fix(make_scene(), fix, make_script())
    dialogue = rebuilt.shots[0].dialogue
    assert dialogue
    assert dialogue.text == LINE
    assert dialogue.delivery == 'slower and louder'
    assert rebuilt.format.duration_s == 11
    assert rebuilt.setting.ambient_level == AmbientLevel.LOW


def test_wan_prompt_quotes_line_verbatim_and_numbers_references_by_order() -> None:
    prompt = render_wan_prompt(make_scene())
    assert f'"{LINE}"' in prompt
    assert 'Jake is Image 1' in prompt
    assert 'Tom is Image 2' in prompt
    assert 'Shot 1 (00:00-00:05)' in prompt
    assert 'Shot 2 (00:05-00:10)' in prompt
    assert 'Tom turns to Jake.' in prompt
    assert 'Negative prompt list: subtitles.' in prompt
