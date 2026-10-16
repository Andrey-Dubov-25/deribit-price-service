from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    LatestPriceResponse,
    PriceItem,
    PriceListResponse,
    Ticker,
)
from app.db.session import get_session
from app.repositories.price_repository import PriceRepository

router = APIRouter(prefix="/prices", tags=["prices"])


def get_price_repository(
    session: AsyncSession = Depends(get_session),
) -> PriceRepository:
    """FastAPI-зависимость: репозиторий цен."""
    return PriceRepository(session)


@router.get("", response_model=PriceListResponse)
async def get_all_prices(
    ticker: Ticker = Query(..., description="Тикер валюты"),
    repository: PriceRepository = Depends(get_price_repository),
) -> PriceListResponse:
    """Все сохранённые цены по указанному тикеру."""
    prices = await repository.get_all_by_ticker(ticker.value)
    return PriceListResponse(
        ticker=ticker.value,
        items=[PriceItem.model_validate(price) for price in prices],
    )


@router.get("/latest", response_model=LatestPriceResponse)
async def get_latest_price(
    ticker: Ticker = Query(..., description="Тикер валюты"),
    repository: PriceRepository = Depends(get_price_repository),
) -> LatestPriceResponse:
    """Последняя сохранённая цена по указанному тикеру."""
    price = await repository.get_latest_by_ticker(ticker.value)
    if price is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Цены по тикеру {ticker.value} не найдены",
        )
    return LatestPriceResponse(
        ticker=price.ticker,
        price=price.price,
        timestamp=price.timestamp,
    )


@router.get("/filter", response_model=PriceListResponse)
async def get_prices_by_period(
    ticker: Ticker = Query(..., description="Тикер валюты"),
    from_ts: int | None = Query(
        None, ge=0, description="UNIX timestamp, начало"
    ),
    to_ts: int | None = Query(None, ge=0, description="UNIX timestamp, конец"),
    repository: PriceRepository = Depends(get_price_repository),
) -> PriceListResponse:
    """Цены по тикеру с фильтром по UNIX-времени (включительно)."""
    if from_ts is not None and to_ts is not None and from_ts > to_ts:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="from_ts должен быть меньше или равен to_ts",
        )

    prices = await repository.get_by_ticker_and_period(
        ticker=ticker.value, from_ts=from_ts, to_ts=to_ts
    )
    return PriceListResponse(
        ticker=ticker.value,
        items=[PriceItem.model_validate(price) for price in prices],
    )
