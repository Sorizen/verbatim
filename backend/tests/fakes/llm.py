import json
from collections.abc import Callable
from typing import Any

from app.enums import AgentRole
from app.providers.types import ChatMessage, StructuredReply, TextPart
from tests.fakes import llm_builders

USER_ROLE = 'user'
BUILDERS: dict[AgentRole, Callable[[dict[str, Any]], dict[str, Any]]] = {
    AgentRole.PRODUCER: llm_builders.build_brief,
    AgentRole.SCREENWRITER: llm_builders.build_script,
    AgentRole.SCRIPT_CRITIC: llm_builders.build_critique,
    AgentRole.CASTING: llm_builders.build_cast,
    AgentRole.PORTRAIT_JUDGE: llm_builders.build_portrait_review,
    AgentRole.DIRECTOR: llm_builders.build_scene,
    AgentRole.SHOT_FIXER: llm_builders.build_shot_fix,
    AgentRole.SCENE_JUDGE: llm_builders.build_scene_judgment,
}


def first_user_payload(messages: list[ChatMessage]) -> dict[str, Any]:
    message = next(message for message in messages if message.role == USER_ROLE)
    text = next(part.text for part in message.parts if isinstance(part, TextPart))
    payload: dict[str, Any] = json.loads(text)
    return payload


class FakeLlm:
    async def complete(
        self,
        *,
        model: str,
        messages: list[ChatMessage],
        schema_name: str,
        json_schema: dict[str, Any],
    ) -> StructuredReply:
        build = BUILDERS[AgentRole(schema_name)]
        return StructuredReply(content=json.dumps(build(first_user_payload(messages))), cost_usd=0.0)
