from fastapi import APIRouter

from app.api.routers import health_router, run_router

api_router = APIRouter()
api_router.include_router(run_router)
api_router.include_router(health_router)

__all__ = ['api_router']
