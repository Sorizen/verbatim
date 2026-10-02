import base64

from app.constants import IMAGE_OUTPUT_FORMAT, IMAGES_PATH
from app.exceptions import ProviderError
from app.providers.openrouter.http import OpenRouterHttp
from app.providers.openrouter.schemas import ImageGeneration, cost_of
from app.providers.types import GeneratedImage


class OpenRouterImages:
    def __init__(self, http: OpenRouterHttp) -> None:
        self._http = http

    async def generate(self, *, model: str, prompt: str, aspect_ratio: str) -> GeneratedImage:
        body = {'model': model, 'prompt': prompt, 'aspect_ratio': aspect_ratio, 'output_format': IMAGE_OUTPUT_FORMAT}
        generation = ImageGeneration.model_validate(await self._http.post_json(IMAGES_PATH, body))
        if not generation.data:
            raise ProviderError(f'{model} returned no image')
        return GeneratedImage(data=base64.b64decode(generation.data[0].b64_json), cost_usd=cost_of(generation.usage))
