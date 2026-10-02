from pathlib import Path

from app.constants import JPEG_MIME_TYPE, JUDGE_MODEL
from app.enums import AgentRole
from app.pipeline.agents.caller import AgentResult, StructuredCaller
from app.pipeline.contracts import CastMember, PortraitReview
from app.providers.types import ImagePart
from app.utils import file_to_data_url


class PortraitJudge:
    def __init__(self, caller: StructuredCaller) -> None:
        self._caller = caller

    async def review(self, *, member: CastMember, portrait_path: Path) -> AgentResult[PortraitReview]:
        return await self._caller.call(
            role=AgentRole.PORTRAIT_JUDGE,
            model=JUDGE_MODEL,
            schema=PortraitReview,
            payload={'character': member.model_dump(mode='json', exclude={'portrait_prompt'})},
            media=[ImagePart(data_url=file_to_data_url(portrait_path, JPEG_MIME_TYPE))],
        )
