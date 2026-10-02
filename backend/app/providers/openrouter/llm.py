from typing import Any

from app.constants import CHAT_COMPLETIONS_PATH, JSON_SCHEMA_RESPONSE_TYPE
from app.exceptions import ProviderError
from app.providers.openrouter.http import OpenRouterHttp
from app.providers.openrouter.messages import serialize_message
from app.providers.openrouter.schemas import ChatCompletion, cost_of
from app.providers.types import ChatMessage, StructuredReply


class OpenRouterLlm:
    def __init__(self, http: OpenRouterHttp) -> None:
        self._http = http

    async def complete(
        self,
        *,
        model: str,
        messages: list[ChatMessage],
        schema_name: str,
        json_schema: dict[str, Any],
    ) -> StructuredReply:
        body = {
            'model': model,
            'messages': [serialize_message(message) for message in messages],
            'response_format': {
                'type': JSON_SCHEMA_RESPONSE_TYPE,
                'json_schema': {'name': schema_name, 'strict': True, 'schema': json_schema},
            },
            'provider': {'require_parameters': True},
        }
        completion = ChatCompletion.model_validate(await self._http.post_json(CHAT_COMPLETIONS_PATH, body))
        content = completion.choices[0].message.content if completion.choices else None
        if not content:
            raise ProviderError(f'{model} returned an empty completion for {schema_name}')
        return StructuredReply(content=content, cost_usd=cost_of(completion.usage))
