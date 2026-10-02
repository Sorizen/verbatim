import tempfile
from pathlib import Path

from app.providers.types import GeneratedImage
from tests.fakes.media import render_still

PALETTE = ('0x6b4a3a', '0x3a4f6b', '0x5a3a6b', '0x3a6b52')
PORTRAIT_WIDTH = 576
PORTRAIT_HEIGHT = 1024
FAKE_FILE_NAME = 'portrait.jpg'


class FakeImages:
    def __init__(self) -> None:
        self._count = 0

    async def generate(self, *, model: str, prompt: str, aspect_ratio: str) -> GeneratedImage:
        color = PALETTE[self._count % len(PALETTE)]
        self._count += 1
        with tempfile.TemporaryDirectory() as directory:
            path = await render_still(
                Path(directory) / FAKE_FILE_NAME, color=color, width=PORTRAIT_WIDTH, height=PORTRAIT_HEIGHT
            )
            return GeneratedImage(data=path.read_bytes(), cost_usd=0.0)
