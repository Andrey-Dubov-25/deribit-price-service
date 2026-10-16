import asyncio
import json
import logging
from decimal import Decimal, InvalidOperation

import aiohttp

from app.clients.exceptions import DeribitClientError

logger = logging.getLogger(__name__)


class DeribitClient:
    """Асинхронный клиент публичного API Deribit."""

    INDEX_PRICE_PATH = "/api/v2/public/get_index_price"

    def __init__(
        self,
        base_url: str,
        timeout: int = 10,
        max_retries: int = 3,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Создать клиент.

        Если сессия передана снаружи, клиент её не закрывает — это
        ответственность того, кто её создал.
        """
        self._base_url = base_url.rstrip("/")
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._max_retries = max_retries
        self._session = session
        self._owns_session = session is None

    async def __aenter__(self) -> "DeribitClient":
        """Открыть клиент: создать HTTP-сессию, если её не передали."""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self

    async def __aexit__(self, *_: object) -> None:
        """Закрыть клиент: закрыть сессию, если она наша."""
        if self._owns_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def get_index_price(self, index_name: str) -> Decimal:
        """Получить index price для указанного индекса (например, btc_usd)."""
        url = f"{self._base_url}{self.INDEX_PRICE_PATH}"
        params = {"index_name": index_name}

        last_error: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                return await self._request_index_price(url, params)
            except DeribitClientError as exc:
                last_error = exc
                logger.warning(
                    (
                        "Запрос к Deribit не удался (попытка %d/%d, "
                        "индекс=%s): %s"
                    ),
                    attempt,
                    self._max_retries,
                    index_name,
                    exc,
                )
                if attempt < self._max_retries:
                    await asyncio.sleep(0.5 * 2 ** (attempt - 1))

        raise DeribitClientError(
                f"Запрос к Deribit не удался после {self._max_retries} "
                f"попыток: {last_error}"
        )

    async def _request_index_price(
        self, url: str, params: dict[str, str]
    ) -> Decimal:
        """Выполнить один HTTP-запрос и вернуть цену из ответа."""
        if self._session is None:
            raise DeribitClientError("HTTP-сессия не инициализирована")

        try:
            async with self._session.get(url, params=params) as response:
                if response.status != 200:
                    raise DeribitClientError(
                        f"Неожиданный HTTP-статус: {response.status}"
                    )
                payload = await response.json()
        except TimeoutError as exc:
            raise DeribitClientError("Таймаут запроса к Deribit") from exc
        except json.JSONDecodeError as exc:
            raise DeribitClientError(
                "Ответ не является валидным JSON"
            ) from exc
        except aiohttp.ClientError as exc:
            raise DeribitClientError(f"HTTP-ошибка: {exc}") from exc

        result = payload.get("result")
        if not isinstance(result, dict) or "index_price" not in result:
            raise DeribitClientError(f"Неверная структура ответа: {payload}")

        try:
            return Decimal(str(result["index_price"]))
        except (InvalidOperation, TypeError) as exc:
            raise DeribitClientError(
                f"Некорректное значение index_price: {result['index_price']}"
            ) from exc
