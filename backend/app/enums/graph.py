from enum import StrEnum


class NodeName(StrEnum):
    BRIEF = 'brief'
    SCRIPT = 'script'
    SCRIPT_CHECK = 'script_check'
    SCRIPT_REVIEW = 'script_review'
    CAST = 'cast'
    PORTRAITS = 'portraits'
    PORTRAIT_CHECK = 'portrait_check'
    PORTRAIT_REVIEW = 'portrait_review'
    SCENE = 'scene'
    RENDER = 'render'
    SCENE_CHECK = 'scene_check'
    SHOT_FIX = 'shot_fix'
    FINALIZE = 'finalize'
    TAKE_REVIEW = 'take_review'
    REJECTED = 'rejected'
