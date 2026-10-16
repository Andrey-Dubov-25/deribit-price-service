import pytest
from aioresponses import aioresponses
from fastapi import status

from app.clients.deribit_client import DeribitClient
from app.clients.exceptions import DeribitClientError
from tests.constants import (
    BASE_URL,
    BTC_PRICE_SAMPLE,
    BTC_USD,
    BTC_USD_INDEX_PRICE_URL,
    TEST_MAX_RETRIES,
)


async def test_get_index_price_returns_decimal() -> None:
    """Успешный ответ Deribit: возвращается Decimal с ожидаемой ценой."""
    with aioresponses() as mocked:
        mocked.get(
            BTC_USD_INDEX_PRICE_URL,
            payload={"result": {"index_price": 42000.5}},
        )

        async with DeribitClient(
            base_url=BASE_URL, max_retries=TEST_MAX_RETRIES
        ) as client:
            price = await client.get_index_price(BTC_USD)

    assert price == BTC_PRICE_SAMPLE


async def test_get_index_price_raises_on_http_error() -> None:
    """HTTP-ошибка от Deribit: клиент бросает DeribitClientError."""
    with aioresponses() as mocked:
        mocked.get(
            BTC_USD_INDEX_PRICE_URL,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

        async with DeribitClient(
            base_url=BASE_URL, max_retries=TEST_MAX_RETRIES
        ) as client:
            with pytest.raises(DeribitClientError):
                await client.get_index_price(BTC_USD)


async def test_get_index_price_raises_on_malformed_response() -> None:
    """Некорректная структура ответа: клиент бросает DeribitClientError."""
    with aioresponses() as mocked:
        mocked.get(
            BTC_USD_INDEX_PRICE_URL,
            payload={"result": {}},
        )

        async with DeribitClient(
            base_url=BASE_URL, max_retries=TEST_MAX_RETRIES
        ) as client:
            with pytest.raises(DeribitClientError):
                await client.get_index_price(BTC_USD)