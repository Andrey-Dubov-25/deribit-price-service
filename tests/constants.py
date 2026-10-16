"""Общие константы для тестов."""

from decimal import Decimal

BASE_URL = "https://www.deribit.com"
INDEX_PRICE_PATH = "/api/v2/public/get_index_price"
INDEX_PRICE_URL = f"{BASE_URL}{INDEX_PRICE_PATH}"
BTC_USD_INDEX_PRICE_URL = f"{INDEX_PRICE_URL}?index_name=btc_usd"


BTC_USD = "btc_usd"
ETH_USD = "eth_usd"
"""Тикеры."""


TEST_MAX_RETRIES = 1
"""Одна попытка: тест не должен ждать retry-паузы."""


BTC_PRICE_SAMPLE = Decimal("42000.5")
"""Цена btc_usd для happy-path теста клиента."""

ETH_PRICE_SAMPLE = Decimal("2500.1")
"""Цена eth_usd для теста сервиса."""
