from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import settings


def create_engine(*, pooled: bool = True) -> AsyncEngine:
    if pooled:
        return create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    return create_async_engine(settings.SQLALCHEMY_DATABASE_URI, poolclass=NullPool)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


engine = create_engine()
SessionLocal = create_session_factory(engine)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
