import json
from typing import Any

import pytest

from app.enums import AgentRole
from app.exceptions import ContractViolationError
from app.pipeline.agents import StructuredCaller
from app.pipeline.contracts import ShotFix
from app.providers.types import ChatMessage, StructuredReply

VALID_FIX = {
    'shot_id': 's1',
    'duration_s': 6,
    'delivery': 'slower and clearer',
    'ambient_level': 'low',
    'camera': {'size': 'close-up', 'movement': 'static', 'angle': 'eye-level'},
    'reason': 'truncated',
}
QUOTED_FIX = {**VALID_FIX, 'delivery': 'he says "nice hat" slowly'}


class ScriptedLlm:
    def __init__(self, replies: list[dict[str, Any]]) -> None:
        self.replies = replies
        self.calls: list[list[ChatMessage]] = []

    async def complete(
        self,
        *,
        model: str,
        messages: list[ChatMessage],
        schema_name: str,
        json_schema: dict[str, Any],
    ) -> StructuredReply:
        self.calls.append(messages)
        return StructuredReply(content=json.dumps(self.replies[len(self.calls) - 1]), cost_usd=0.01)


async def test_reasks_after_quoted_dialogue_and_sums_cost() -> None:
    llm = ScriptedLlm([QUOTED_FIX, VALID_FIX])
    result = await StructuredCaller(llm).call(role=AgentRole.SHOT_FIXER, model='m', schema=ShotFix, payload={})
    assert result.value.delivery == 'slower and clearer'
    assert result.cost_usd == pytest.approx(0.02)
    assert len(llm.calls) == 2
    assert len(llm.calls[1]) == len(llm.calls[0]) + 2


async def test_gives_up_after_schema_retries() -> None:
    llm = ScriptedLlm([QUOTED_FIX] * 3)
    with pytest.raises(ContractViolationError):
        await StructuredCaller(llm).call(role=AgentRole.SHOT_FIXER, model='m', schema=ShotFix, payload={})
