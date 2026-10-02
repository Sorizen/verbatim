from app.constants import MAX_SCENE_SECONDS, MIN_SCENE_SECONDS, VIDEO_ASPECT_TOLERANCE
from app.media import MediaInfo
from app.pipeline.contracts import FormatCheck

TARGET_ASPECT = 9 / 16
DURATION_TOLERANCE_SECONDS = 0.5


def build_format_check(info: MediaInfo) -> FormatCheck:
    aspect = info.width / info.height if info.height else 0.0
    low = MIN_SCENE_SECONDS - DURATION_TOLERANCE_SECONDS
    high = MAX_SCENE_SECONDS + DURATION_TOLERANCE_SECONDS
    return FormatCheck(
        aspect_ok=abs(aspect - TARGET_ASPECT) <= VIDEO_ASPECT_TOLERANCE,
        duration_s=round(info.duration_s, 2),
        duration_ok=low <= info.duration_s <= high,
        has_audio=info.has_audio,
    )
