import asyncio
from pathlib import Path
from typing import Any

import anyio
import httpx

from app.constants import (
    BACKOFF_BASE_SECONDS,
    BACKOFF_MAX_SECONDS,
    HTTP_TIMEOUT_SECONDS,
    MAX_HTTP_RETRIES,
    RETRYABLE_STATUS_CODES,
)
from app.exceptions import ProviderError

AUTHORIZATION_HEADER = 'Authorization'
BEARER_TEMPLATE = 'Bearer {api_key}'
ERROR_TEMPLATE = '{method} {path} failed with {status}: {body}'
ERROR_BODY_LIMIT = 500


def backoff_seconds(attempt: int) -> float:
    return float(min(BACKOFF_BASE_SECONDS * 2**attempt, BACKOFF_MAX_SECONDS))


class OpenRouterHttp:
    def __init__(self, *, api_key: str, base_url: str) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={AUTHORIZATION_HEADER: BEARER_TEMPLATE.format(api_key=api_key)},
            timeout=HTTP_TIMEOUT_SECONDS,
        )

    async def post_json(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        response = await self._send('POST', path, json=body)
        payload: dict[str, Any] = response.json()
        return payload

    async def get_json(self, path: str) -> dict[str, Any]:
        response = await self._send('GET', path)
        payload: dict[str, Any] = response.json()
        return payload

    async def download(self, path: str, destination: Path, params: dict[str, Any] | None = None) -> None:
        await anyio.Path(destination.parent).mkdir(parents=True, exist_ok=True)
        response = await self._send('GET', path, params=params)
        await anyio.Path(destination).write_bytes(response.content)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _send(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        for attempt in range(MAX_HTTP_RETRIES + 1):
            try:
                response = await self._client.request(method, path, **kwargs)
            except httpx.TransportError as error:
                if attempt == MAX_HTTP_RETRIES:
                    raise ProviderError(f'{method} {path}: {error}') from error
                await asyncio.sleep(backoff_seconds(attempt))
                continue
            if response.status_code in RETRYABLE_STATUS_CODES and attempt < MAX_HTTP_RETRIES:
                await asyncio.sleep(backoff_seconds(attempt))
                continue
            if response.is_error:
                raise ProviderError(
                    ERROR_TEMPLATE.format(
                        method=method, path=path, status=response.status_code, body=response.text[:ERROR_BODY_LIMIT]
                    )
                )
            return response
        raise ProviderError(f'{method} {path}: retries exhausted')
