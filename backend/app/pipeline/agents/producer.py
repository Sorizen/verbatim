from app.constants import LLM_MODEL
from app.enums import AgentRole
from app.pipeline.agents.caller import AgentResult, StructuredCaller
from app.pipeline.contracts import BriefDraft


class Producer:
    def __init__(self, caller: StructuredCaller) -> None:
        self._caller = caller

    async def write_brief(self, *, idea: str, locked_lines: list[str]) -> AgentResult[BriefDraft]:
        return await self._caller.call(
            role=AgentRole.PRODUCER,
            model=LLM_MODEL,
            schema=BriefDraft,
            payload={'idea': idea, 'locked_lines': locked_lines},
        )
