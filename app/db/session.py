from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine(database_url: str) -> AsyncEngine:
    """Создать async-движок SQLAlchemy."""
    return create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
        future=True,
    )


def create_session_factory(
        engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
    """Создать фабрику async-сессий."""
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
    )


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """FastAPI-зависимость: отдаёт сессию из фабрики, лежащей в app.state."""
    session_factory: async_sessionmaker[
        AsyncSession
    ] = request.app.state.session_factory
    async with session_factory() as session:
        yield session
