from app.constants import LLM_MODEL
from app.enums import AgentRole
from app.pipeline.agents.caller import AgentResult, StructuredCaller
from app.pipeline.contracts import Brief, Cast, Script
from app.pipeline.rules import check_cast_matches_brief


class CastingDirector:
    def __init__(self, caller: StructuredCaller) -> None:
        self._caller = caller

    async def cast(self, *, brief: Brief, script: Script) -> AgentResult[Cast]:
        return await self._caller.call(
            role=AgentRole.CASTING,
            model=LLM_MODEL,
            schema=Cast,
            payload={'brief': brief.model_dump(mode='json'), 'script': script.model_dump(mode='json')},
            check=lambda cast: check_cast_matches_brief(cast, brief),
        )
