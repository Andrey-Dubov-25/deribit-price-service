from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Price


class PriceRepository:
    """Репозиторий для работы с таблицей цен."""

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def add(self, ticker: str, price: Decimal, timestamp: int) -> Price:
        """Сохранить новую цену и вернуть созданную запись."""
        entry = Price(ticker=ticker, price=price, timestamp=timestamp)
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def get_all_by_ticker(self, ticker: str) -> list[Price]:
        """Вернуть все сохранённые цены по тикеру (от новых к старым)."""
        result = await self._session.execute(
            select(Price)
            .where(Price.ticker == ticker)
            .order_by(Price.timestamp.desc())
        )
        return list(result.scalars().all())

    async def get_latest_by_ticker(self, ticker: str) -> Price | None:
        """Вернуть последнюю сохранённую цену по тикеру."""
        result = await self._session.execute(
            select(Price)
            .where(Price.ticker == ticker)
            .order_by(Price.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_ticker_and_period(
        self,
        ticker: str,
        from_ts: int | None,
        to_ts: int | None,
    ) -> list[Price]:
        """Вернуть цены по тикеру с фильтром по UNIX-времени (включительно)."""
        query = select(Price).where(Price.ticker == ticker)
        if from_ts is not None:
            query = query.where(Price.timestamp >= from_ts)
        if to_ts is not None:
            query = query.where(Price.timestamp <= to_ts)
        query = query.order_by(Price.timestamp.desc())

        result = await self._session.execute(query)
        return list(result.scalars().all())
