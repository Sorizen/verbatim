from enum import StrEnum


class ShotSize(StrEnum):
    CLOSE_UP = 'close-up'
    MEDIUM = 'medium'
    WIDE = 'wide'


class CameraMovement(StrEnum):
    STATIC = 'static'
    PUSH_IN = 'push-in'
    PAN = 'pan'
    HANDHELD = 'handheld'


class CameraAngle(StrEnum):
    EYE_LEVEL = 'eye-level'
    LOW = 'low'
    HIGH = 'high'
    OVER_SHOULDER = 'over-shoulder'
