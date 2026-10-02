import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from app.constants import MAX_SCHEMA_RETRIES
from app.enums import AgentRole
from app.exceptions import ContractViolationError
from app.pipeline.contracts import Contract
from app.pipeline.prompts import load_prompt
from app.providers.protocols import LlmClient
from app.providers.types import ChatMessage, ContentPart, TextPart
from app.utils import strict_json_schema

RETRY_INSTRUCTION = (
    'Your previous answer did not pass validation. Fix exactly these errors and return the whole JSON again:\n{errors}'
)
CONTRACT_ERROR_TEMPLATE = '{role} returned invalid {schema} after {attempts} attempts: {errors}'


@dataclass(frozen=True)
class AgentResult[T: Contract]:
    value: T
    cost_usd: float


def build_messages(role: AgentRole, payload: dict[str, Any], media: Sequence[ContentPart]) -> list[ChatMessage]:
    return [
        ChatMessage(role='system', parts=[TextPart(text=load_prompt(role))]),
        ChatMessage(role='user', parts=[TextPart(text=json.dumps(payload, ensure_ascii=False)), *media]),
    ]


def build_retry_messages(reply: str, errors: str) -> list[ChatMessage]:
    return [
        ChatMessage(role='assistant', parts=[TextPart(text=reply)]),
        ChatMessage(role='user', parts=[TextPart(text=RETRY_INSTRUCTION.format(errors=errors))]),
    ]


class StructuredCaller:
    def __init__(self, llm: LlmClient) -> None:
        self._llm = llm

    async def call[T: Contract](
        self,
        *,
        role: AgentRole,
        model: str,
        schema: type[T],
        payload: dict[str, Any],
        media: Sequence[ContentPart] = (),
        check: Callable[[T], None] | None = None,
    ) -> AgentResult[T]:
        messages = build_messages(role, payload, media)
        json_schema = strict_json_schema(schema)
        cost = 0.0
        errors = ''
        for _ in range(MAX_SCHEMA_RETRIES + 1):
            reply = await self._llm.complete(
                model=model, messages=messages, schema_name=role.value, json_schema=json_schema
            )
            cost += reply.cost_usd
            try:
                value = schema.model_validate_json(reply.content)
                if check:
                    check(value)
                return AgentResult(value=value, cost_usd=cost)
            except (ValidationError, ContractViolationError) as error:
                errors = str(error)
                messages = [*messages, *build_retry_messages(reply.content, errors)]
        raise ContractViolationError(
            CONTRACT_ERROR_TEMPLATE.format(
                role=role.value, schema=schema.__name__, attempts=MAX_SCHEMA_RETRIES + 1, errors=errors
            )
        )
