from app.constants import LLM_MODEL
from app.enums import AgentRole
from app.pipeline.agents.caller import AgentResult, StructuredCaller
from app.pipeline.contracts import Brief, Cast, SceneDraft, Script
from app.pipeline.rules import check_draft_matches_script


class Director:
    def __init__(self, caller: StructuredCaller) -> None:
        self._caller = caller

    async def stage(self, *, brief: Brief, script: Script, cast: Cast) -> AgentResult[SceneDraft]:
        return await self._caller.call(
            role=AgentRole.DIRECTOR,
            model=LLM_MODEL,
            schema=SceneDraft,
            payload={
                'brief': brief.model_dump(mode='json'),
                'script': script.model_dump(mode='json'),
                'cast': cast.model_dump(mode='json', exclude={'characters': {'__all__': {'portrait_prompt'}}}),
            },
            check=lambda draft: check_draft_matches_script(draft, script),
        )
