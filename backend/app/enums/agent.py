from enum import StrEnum


class AgentRole(StrEnum):
    PRODUCER = 'producer'
    SCREENWRITER = 'screenwriter'
    SCRIPT_CRITIC = 'script_critic'
    CASTING = 'casting'
    PORTRAIT_JUDGE = 'portrait_judge'
    DIRECTOR = 'director'
    SHOT_FIXER = 'shot_fixer'
    SCENE_JUDGE = 'scene_judge'
