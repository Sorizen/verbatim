from enum import StrEnum


class RunStatus(StrEnum):
    QUEUED = 'queued'
    RUNNING = 'running'
    DONE = 'done'
    NEEDS_REVIEW = 'needs_review'
    FAILED = 'failed'


class StepName(StrEnum):
    BRIEF = 'brief'
    SCRIPT = 'script'
    SCRIPT_CHECK = 'script_check'
    CAST = 'cast'
    PORTRAITS = 'portraits'
    PORTRAIT_CHECK = 'portrait_check'
    SCENE = 'scene'
    RENDER = 'render'
    SCENE_CHECK = 'scene_check'
    SHOT_FIX = 'shot_fix'
    FINAL = 'final'


class StepStatus(StrEnum):
    RUNNING = 'running'
    OK = 'ok'
    REJECTED = 'rejected'
    FAILED = 'failed'
