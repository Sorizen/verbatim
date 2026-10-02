from typing import Any

from app.constants import LLM_MODEL
from app.enums import AgentRole
from app.pipeline.agents.caller import AgentResult, StructuredCaller
from app.pipeline.contracts import Brief, Critique, ScriptDraft
from app.pipeline.rules import check_locked_indexes


def build_feedback(critique: Critique | None) -> dict[str, Any] | None:
    if not critique:
        return None
    return critique.model_dump(mode='json', include={'rule_violations', 'review'})


class Screenwriter:
    def __init__(self, caller: StructuredCaller) -> None:
        self._caller = caller

    async def write_script(self, *, brief: Brief, feedback: Critique | None) -> AgentResult[ScriptDraft]:
        return await self._caller.call(
            role=AgentRole.SCREENWRITER,
            model=LLM_MODEL,
            schema=ScriptDraft,
            payload={
                'brief': brief.model_dump(mode='json', exclude={'locked_lines'}),
                'locked_lines': [{'index': index, 'text': text} for index, text in enumerate(brief.locked_lines)],
                'feedback': build_feedback(feedback),
            },
            check=lambda draft: check_locked_indexes(draft, len(brief.locked_lines)),
        )
