from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers.prices import router as prices_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import create_engine, create_session_factory

API_V1_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Управление жизненным циклом приложения: создаём и закрываем ресурсы."""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    application.state.engine = engine
    application.state.session_factory = create_session_factory(engine)

    yield

    await engine.dispose()


def create_app() -> FastAPI:
    """Создать и настроить FastAPI-приложение."""
    settings = get_settings()
    setup_logging(settings.log_level)

    application = FastAPI(
        title="Deribit Price Service",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    @application.get(f"{API_V1_PREFIX}/health", tags=["health"])
    async def health() -> dict[str, str]:
        """Проверка работоспособности сервиса."""
        return {"status": "ok"}

    application.include_router(prices_router, prefix=API_V1_PREFIX)

    return application


app = create_app()