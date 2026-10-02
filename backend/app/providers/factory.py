from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.config import settings
from app.constants import MISSING_API_KEY_MESSAGE
from app.exceptions import ProviderError
from app.providers.openrouter import OpenRouterHttp, OpenRouterImages, OpenRouterLlm, OpenRouterSpeech, OpenRouterVideos
from app.providers.protocols import Providers


@asynccontextmanager
async def open_providers() -> AsyncIterator[Providers]:
    api_key = settings.OPENROUTER_API_KEY.get_secret_value()
    if not api_key:
        raise ProviderError(MISSING_API_KEY_MESSAGE)
    http = OpenRouterHttp(api_key=api_key, base_url=settings.OPENROUTER_BASE_URL)
    try:
        yield Providers(
            llm=OpenRouterLlm(http),
            images=OpenRouterImages(http),
            videos=OpenRouterVideos(http),
            speech=OpenRouterSpeech(http),
        )
    finally:
        await http.aclose()
