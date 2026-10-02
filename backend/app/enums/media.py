from enum import StrEnum


class VideoResolution(StrEnum):
    P480 = '480p'
    P720 = '720p'
    P1080 = '1080p'


class VideoJobStatus(StrEnum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'


class AmbientLevel(StrEnum):
    NORMAL = 'normal'
    LOW = 'low'
    NONE = 'none'
