import logging
import time
from decimal import Decimal

from app.clients.deribit_client import DeribitClient
from app.clients.exceptions import DeribitClientError
from app.repositories.price_repository import PriceRepository

logger = logging.getLogger(__name__)


class PriceService:
    """Бизнес-логика: забрать цены с биржи и сохранить их."""

    def __init__(
        self,
        client: DeribitClient,
        repository: PriceRepository,
    ) -> None:
        self._client = client
        self._repository = repository

    async def fetch_and_store_prices(
            self, tickers: list[str]
        ) -> dict[str, Decimal]:
        """Забрать цены по тикерам и сохранить их в БД."""
        result: dict[str, Decimal] = {}
        timestamp = int(time.time())

        for ticker in tickers:
            try:
                price = await self._client.get_index_price(ticker)
            except DeribitClientError as exc:
                logger.error("Не удалось получить цену %s: %s", ticker, exc)
                continue

            await self._repository.add(
                ticker=ticker,
                price=price,
                timestamp=timestamp,
            )
            result[ticker] = price
            logger.info("Сохранена цена %s: %s", ticker, price)

        return result
