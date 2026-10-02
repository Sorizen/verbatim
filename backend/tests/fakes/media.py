from pathlib import Path

import anyio

from app.constants import FFMPEG_BINARY
from app.media.process import run_tool

FRAME_RATE = 24
TONE_FREQUENCY_HZ = 220


async def render_still(destination: Path, *, color: str, width: int, height: int) -> Path:
    await anyio.Path(destination.parent).mkdir(parents=True, exist_ok=True)
    await run_tool(
        FFMPEG_BINARY,
        [
            '-y',
            '-v',
            'error',
            '-f',
            'lavfi',
            '-i',
            f'color=c={color}:s={width}x{height}',
            '-frames:v',
            '1',
            str(destination),
        ],
    )
    return destination


async def render_test_video(
    destination: Path,
    *,
    duration_s: int,
    width: int,
    height: int,
    color: str,
    comment: str,
) -> Path:
    await anyio.Path(destination.parent).mkdir(parents=True, exist_ok=True)
    await run_tool(
        FFMPEG_BINARY,
        [
            '-y',
            '-v',
            'error',
            '-f',
            'lavfi',
            '-i',
            f'color=c={color}:s={width}x{height}:d={duration_s}:r={FRAME_RATE}',
            '-f',
            'lavfi',
            '-i',
            f'sine=frequency={TONE_FREQUENCY_HZ}:duration={duration_s}',
            '-shortest',
            '-c:v',
            'libx264',
            '-pix_fmt',
            'yuv420p',
            '-c:a',
            'aac',
            '-metadata',
            f'comment={comment}',
            str(destination),
        ],
    )
    return destination
