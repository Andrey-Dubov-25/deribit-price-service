from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class Ticker(StrEnum):
    """Поддерживаемые тикеры."""

    BTC_USD = "btc_usd"
    ETH_USD = "eth_usd"


class PriceItem(BaseModel):
    """Одна сохранённая цена."""

    ticker: str
    price: Decimal
    timestamp: int

    model_config = ConfigDict(from_attributes=True)


class PriceListResponse(BaseModel):
    """Список сохранённых цен."""

    ticker: str
    items: list[PriceItem]


class LatestPriceResponse(BaseModel):
    """Последняя цена по тикеру."""

    ticker: str
    price: Decimal
    timestamp: int
