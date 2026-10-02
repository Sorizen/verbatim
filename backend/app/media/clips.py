from pathlib import Path

import anyio

from app.constants import FFMPEG_BINARY
from app.media.process import run_tool

FRAME_NAME_PATTERN = 'frame-%03d.jpg'
FRAME_GLOB = 'frame-*.jpg'
AUDIO_BITRATE = '128k'


async def extract_audio(video: Path, destination: Path) -> Path:
    await anyio.Path(destination.parent).mkdir(parents=True, exist_ok=True)
    await run_tool(
        FFMPEG_BINARY,
        ['-y', '-v', 'error', '-i', str(video), '-vn', '-map_metadata', '0', '-b:a', AUDIO_BITRATE, str(destination)],
    )
    return destination


async def extract_audio_window(video: Path, *, start_s: float, end_s: float, destination: Path) -> Path:
    await anyio.Path(destination.parent).mkdir(parents=True, exist_ok=True)
    await run_tool(
        FFMPEG_BINARY,
        [
            '-y',
            '-v',
            'error',
            '-ss',
            f'{start_s:.3f}',
            '-to',
            f'{end_s:.3f}',
            '-i',
            str(video),
            '-vn',
            '-b:a',
            AUDIO_BITRATE,
            str(destination),
        ],
    )
    return destination


async def extract_frames(
    video: Path,
    *,
    start_s: float,
    end_s: float,
    frames_per_second: int,
    width: int,
    destination_dir: Path,
) -> list[Path]:
    await anyio.Path(destination_dir).mkdir(parents=True, exist_ok=True)
    await run_tool(
        FFMPEG_BINARY,
        [
            '-y',
            '-v',
            'error',
            '-ss',
            f'{start_s:.3f}',
            '-to',
            f'{end_s:.3f}',
            '-i',
            str(video),
            '-vf',
            f'fps={frames_per_second},scale={width}:-2',
            str(destination_dir / FRAME_NAME_PATTERN),
        ],
    )
    return sorted([Path(frame) async for frame in anyio.Path(destination_dir).glob(FRAME_GLOB)])
