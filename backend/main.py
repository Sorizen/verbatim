from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.api.exception_handlers import base_error_handler
from app.config import settings
from app.constants import API_PREFIX
from app.db import engine
from app.exceptions import BaseError


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    application = FastAPI(title='Holywater micro-scene', lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    application.include_router(api_router, prefix=API_PREFIX)
    application.add_exception_handler(BaseError, base_error_handler)
    return application


app = create_app()
