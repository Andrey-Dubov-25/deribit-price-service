import asyncio
import logging

from app.clients.deribit_client import DeribitClient
from app.core.config import get_settings
from app.db.session import create_engine, create_session_factory
from app.repositories.price_repository import PriceRepository
from app.services.price_service import PriceService
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


async def _fetch_and_store() -> dict[str, str]:
    """Асинхронная логика: сходить за ценами и сохранить их в БД."""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)

    try:
        async with session_factory() as session, DeribitClient(
            base_url=settings.deribit_base_url,
            timeout=settings.deribit_request_timeout,
        ) as client:
            repository = PriceRepository(session)
            service = PriceService(client=client, repository=repository)

            prices = await service.fetch_and_store_prices(
                tickers=settings.supported_tickers
            )
            await session.commit()

        return {ticker: str(price) for ticker, price in prices.items()}
    finally:
        await engine.dispose()


@celery_app.task(name="app.tasks.fetch_prices.fetch_and_store_prices")
def fetch_and_store_prices() -> dict[str, str]:
    """Периодическая таска: забрать index price по всем тикерам и сохранить."""
    logger.info("Запуск задачи fetch_and_store_prices")
    try:
        result = asyncio.run(_fetch_and_store())
        logger.info("Получены цены: %s", result)
        return result
    except Exception:
        logger.exception("Задача fetch_and_store_prices завершилась ошибкой")
        raise
