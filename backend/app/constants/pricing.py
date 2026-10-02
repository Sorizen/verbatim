from app.enums import VideoResolution

VIDEO_USD_PER_SECOND: dict[VideoResolution, float] = {
    VideoResolution.P480: 0.05,
    VideoResolution.P720: 0.10,
    VideoResolution.P1080: 0.20,
}
