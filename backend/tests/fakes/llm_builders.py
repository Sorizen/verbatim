import math
from typing import Any

from app.constants import MAX_SCENE_SECONDS, MAX_SHOT_SECONDS, MAX_SHOTS, MAX_WORDS_PER_SECOND
from app.enums import SpeakerVisibility

SALOON_WORD = 'saloon'
DEFAULT_LINES = (
    ('c1', 'Nice hat, big man. Did your mother pick it out?', 'mocking'),
    ('c2', "Say that again and you'll be picking up your teeth.", 'threatening'),
)
CHARACTERS = (
    {'id': 'c1', 'name': 'Jake', 'role': 'the provoker', 'age': 34},
    {'id': 'c2', 'name': 'Big Tom', 'role': 'the one provoked', 'age': 41},
)
VOICES = ('low, dry male voice with a slight drawl', 'deep, rough male voice')
MIN_FAKE_SHOT_SECONDS = 5
SPOKEN_PADDING_SECONDS = 1
PASSING_CRITIC_SCORE = 8
PASSING_JUDGE_SCORE = 8
FULL_PRESENCE_SCORE = 10
TOP_PORTRAIT_SCORE = 5
PORTRAIT_CRITERIA = (
    'description_match',
    'single_subject',
    'adult',
    'clean_frame',
    'face_integrity',
    'reference_quality',
)
FAKE_NOTE = 'fake provider'


def shot_seconds_for(text: str) -> int:
    needed = math.ceil(len(text.split()) / MAX_WORDS_PER_SECOND) + SPOKEN_PADDING_SECONDS
    return min(max(needed, MIN_FAKE_SHOT_SECONDS), MAX_SHOT_SECONDS)


def build_brief(payload: dict[str, Any]) -> dict[str, Any]:
    idea: str = payload['idea']
    saloon = SALOON_WORD in idea.lower()
    return {
        'logline': idea.split('.')[0][:140],
        'genre': 'western' if saloon else 'drama',
        'tone': 'tense',
        'setting': {
            'place': 'a crowded saloon' if saloon else 'a late-night diner',
            'time_of_day': 'night',
            'era': '1880s American frontier' if saloon else 'present day',
        },
        'characters': list(CHARACTERS),
        'target_duration_s': 15,
        'assumptions': [{'field': 'characters', 'value': 'two adult men', 'source': 'inferred'}],
    }


def build_spoken_shot(number: int, speaker: str, text: str, emotion: str, locked_index: int | None) -> dict[str, Any]:
    return {
        'id': f's{number}',
        'beat': f'{speaker} speaks',
        'duration_s': shot_seconds_for(text),
        'line': {
            'speaker': speaker,
            'text': None if locked_index is not None else text,
            'locked_line_index': locked_index,
            'emotion': emotion,
        },
    }


def build_script(payload: dict[str, Any]) -> dict[str, Any]:
    locked: list[dict[str, Any]] = payload['locked_lines']
    shots = []
    for index, item in enumerate(locked):
        speaker, _, emotion = DEFAULT_LINES[index % len(DEFAULT_LINES)]
        shots.append(build_spoken_shot(index + 1, speaker, item['text'], emotion, item['index']))
    for speaker, text, emotion in DEFAULT_LINES[len(locked) :]:
        shots.append(build_spoken_shot(len(shots) + 1, speaker, text, emotion, None))
    total = sum(shot['duration_s'] for shot in shots)
    if len(shots) < MAX_SHOTS and total + MIN_FAKE_SHOT_SECONDS <= MAX_SCENE_SECONDS:
        shots.append(
            {'id': f's{len(shots) + 1}', 'beat': 'The fight begins', 'duration_s': MIN_FAKE_SHOT_SECONDS, 'line': None}
        )
    return {'title': 'The hat', 'shots': shots}


def critic_score() -> dict[str, Any]:
    return {'score': PASSING_CRITIC_SCORE, 'reason': FAKE_NOTE, 'improvements': []}


def build_critique(_: dict[str, Any]) -> dict[str, Any]:
    return {'hook': critic_score(), 'escalation': critic_score(), 'ending': critic_score()}


def build_cast(payload: dict[str, Any]) -> dict[str, Any]:
    characters = payload['brief']['characters']
    return {
        'characters': [
            {
                'id': character['id'],
                'look': f'{character["age"]}-year-old man with a weathered face',
                'wardrobe': 'dusty coat and a hat',
                'voice': VOICES[index % len(VOICES)],
                'portrait_prompt': f'Photoreal vertical portrait of {character["name"]}, plain background, no text',
            }
            for index, character in enumerate(characters)
        ]
    }


def build_portrait_review(_: dict[str, Any]) -> dict[str, Any]:
    return {
        'scores': dict.fromkeys(PORTRAIT_CRITERIA, TOP_PORTRAIT_SCORE),
        'explanations': dict.fromkeys(PORTRAIT_CRITERIA, FAKE_NOTE),
    }


def build_staged_shot(shot: dict[str, Any]) -> dict[str, Any]:
    line = shot['line']
    return {
        'id': shot['id'],
        'camera': {'size': 'medium' if line else 'wide', 'movement': 'static', 'angle': 'eye-level'},
        'action': f'{line["speaker"]} faces the other man' if line else 'c2 swings first and c1 ducks',
        'delivery': 'slow and clear' if line else None,
        'sfx': [],
    }


def build_scene(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        'style': 'photoreal, warm practical light, 35mm film grain',
        'setting': {
            'place': payload['brief']['setting']['place'],
            'light': 'oil lamps',
            'ambient_sound': 'low murmur of patrons',
        },
        'shots': [build_staged_shot(shot) for shot in payload['script']['shots']],
        'negative': ['subtitles or on-screen text', 'extra speaking characters', 'blood', 'weapons'],
    }


def build_shot_fix(payload: dict[str, Any]) -> dict[str, Any]:
    shot_id: str = payload['failed_shot_id']
    shots = payload['scene']['shots']
    total = sum(shot['duration_s'] for shot in shots)
    current = next(shot['duration_s'] for shot in shots if shot['id'] == shot_id)
    longer = current + 1 if total + 1 <= MAX_SCENE_SECONDS and current < MAX_SHOT_SECONDS else current
    return {
        'shot_id': shot_id,
        'duration_s': longer,
        'delivery': 'slower, clearer and louder',
        'ambient_level': 'low',
        'camera': {'size': 'close-up', 'movement': 'static', 'angle': 'eye-level'},
        'reason': 'mumbled',
    }


def build_scene_judgment(payload: dict[str, Any]) -> dict[str, Any]:
    spoken = [shot['id'] for shot in payload['scene']['shots'] if shot['dialogue']]
    return {
        'physics_integrity': PASSING_JUDGE_SCORE,
        'temporal_continuity': PASSING_JUDGE_SCORE,
        'reaction_plausibility': PASSING_JUDGE_SCORE,
        'character_presence_consistency': FULL_PRESENCE_SCORE,
        'on_screen_text': False,
        'artifacts': [],
        'speakers': [{'shot_id': shot_id, 'visibility': SpeakerVisibility.ON_SCREEN.value} for shot_id in spoken],
        'analysis': FAKE_NOTE,
    }
