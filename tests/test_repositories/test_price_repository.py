from decimal import Decimal

from app.repositories.price_repository import PriceRepository
from tests.constants import BTC_USD


async def test_get_latest_by_ticker_returns_highest_timestamp(session) -> None:
    """get_latest_by_ticker возвращает запись с максимальным timestamp."""
    repo = PriceRepository(session)

    await repo.add(BTC_USD, Decimal("100.0"), 1000)
    await repo.add(BTC_USD, Decimal("200.0"), 2000)
    await repo.add(BTC_USD, Decimal("150.0"), 1500)
    await session.commit()

    latest = await repo.get_latest_by_ticker(BTC_USD)

    assert latest is not None
    assert latest.timestamp == 2000
    assert latest.price == Decimal("200.0")