from functools import cache
from pathlib import Path
from string import Template

from app.constants import (
    ADULT_AGE,
    MAX_CHARACTERS,
    MAX_OWN_LINE_WORDS,
    MAX_SCENE_SECONDS,
    MAX_SHOT_SECONDS,
    MAX_SHOTS,
    MAX_WORDS_PER_SECOND,
    MIN_SCENE_SECONDS,
    MIN_SHOT_SECONDS,
    PORTRAIT_MAX_SCORE,
    PORTRAIT_MIN_SCORE,
    PORTRAIT_REJECT_BELOW,
)
from app.enums import AgentRole

PROMPTS_DIR = Path(__file__).parent
PROMPT_SUFFIX = '.md'
PROMPT_VARIABLES: dict[str, object] = {
    'adult_age': ADULT_AGE,
    'max_characters': MAX_CHARACTERS,
    'max_own_line_words': MAX_OWN_LINE_WORDS,
    'max_scene_seconds': MAX_SCENE_SECONDS,
    'max_shot_seconds': MAX_SHOT_SECONDS,
    'max_shots': MAX_SHOTS,
    'max_words_per_second': MAX_WORDS_PER_SECOND,
    'min_scene_seconds': MIN_SCENE_SECONDS,
    'min_shot_seconds': MIN_SHOT_SECONDS,
    'portrait_max_score': PORTRAIT_MAX_SCORE,
    'portrait_min_score': PORTRAIT_MIN_SCORE,
    'portrait_reject_below': PORTRAIT_REJECT_BELOW,
}


@cache
def load_prompt(role: AgentRole) -> str:
    template = Template((PROMPTS_DIR / f'{role.value}{PROMPT_SUFFIX}').read_text())
    return template.substitute(PROMPT_VARIABLES)
