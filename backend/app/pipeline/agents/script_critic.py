from app.constants import LLM_MODEL
from app.enums import AgentRole
from app.pipeline.agents.caller import AgentResult, StructuredCaller
from app.pipeline.contracts import Brief, CritiqueDraft, Script


class ScriptCritic:
    def __init__(self, caller: StructuredCaller) -> None:
        self._caller = caller

    async def review(self, *, brief: Brief, script: Script) -> AgentResult[CritiqueDraft]:
        return await self._caller.call(
            role=AgentRole.SCRIPT_CRITIC,
            model=LLM_MODEL,
            schema=CritiqueDraft,
            payload={'brief': brief.model_dump(mode='json'), 'script': script.model_dump(mode='json')},
        )
