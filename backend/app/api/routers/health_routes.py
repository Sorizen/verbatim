from fastapi import APIRouter

from app.constants import HEALTH_TAG
from app.schema import HealthResponse

HEALTH_OK = 'ok'

router = APIRouter(tags=[HEALTH_TAG])


@router.get('/health', response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status=HEALTH_OK)
