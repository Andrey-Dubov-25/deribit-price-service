from decimal import Decimal

from sqlalchemy import BigInteger, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import PRICE_PRECISION, PRICE_SCALE, TICKER_MAX_LENGTH
from app.db.base import Base


class Price(Base):
    """Сохранённая цена валюты на бирже."""

    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    ticker: Mapped[str] = mapped_column(String(TICKER_MAX_LENGTH))
    price: Mapped[Decimal] = mapped_column(
        Numeric(PRICE_PRECISION, PRICE_SCALE)
    )
    timestamp: Mapped[int] = mapped_column(BigInteger)

    __table_args__ = (
        Index("ix_prices_ticker_timestamp", "ticker", "timestamp"),
    )

    def __repr__(self) -> str:
        return (
            f"<Price ticker={self.ticker} price={self.price} "
            f"ts={self.timestamp}>"
        )
