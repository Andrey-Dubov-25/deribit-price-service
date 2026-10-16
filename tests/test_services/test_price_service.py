from decimal import Decimal
from unittest.mock import AsyncMock

from app.services.price_service import PriceService


async def test_fetch_and_store_prices_saves_each_ticker() -> None:
    """
    Сервис сохраняет цену по каждому тикеру и возвращает словарь
    {ticker: price}.
    """
    client = AsyncMock()
    client.get_index_price.side_effect = [
        Decimal("42000.5"), Decimal("2500.1")
    ]

    repository = AsyncMock()

    service = PriceService(client=client, repository=repository)
    result = await service.fetch_and_store_prices(["btc_usd", "eth_usd"])

    assert result == {
        "btc_usd": Decimal("42000.5"), "eth_usd": Decimal("2500.1")
    }
    assert repository.add.await_count == 2
    assert client.get_index_price.await_count == 2
