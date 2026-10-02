from pathlib import Path

import anyio

from app.constants import FFMPEG_BINARY
from app.media.process import run_tool

JPEG_MAGIC = b'\xff\xd8\xff'
JPEG_QUALITY = '2'
CONVERTED_SUFFIX = '.converted.jpg'


async def ensure_jpeg(path: Path) -> Path:
    if (await anyio.Path(path).read_bytes())[: len(JPEG_MAGIC)] == JPEG_MAGIC:
        return path
    converted = path.with_suffix(CONVERTED_SUFFIX)
    await run_tool(FFMPEG_BINARY, ['-y', '-v', 'error', '-i', str(path), '-q:v', JPEG_QUALITY, str(converted)])
    await anyio.Path(converted).replace(path)
    return path
