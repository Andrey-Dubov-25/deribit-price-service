# Deribit Price Service

Сервис раз в минуту забирает index price (`btc_usd`, `eth_usd`) с биржи
[Deribit](https://docs.deribit.com/) и сохраняет в PostgreSQL.
Данные доступны через REST API на FastAPI.

## Стек

Python 3.12, FastAPI, SQLAlchemy 2 (async), Alembic, Celery + Redis,
aiohttp, PostgreSQL 16, Docker Compose, pytest, ruff.

## Быстрый старт

1. Скопируйте настройки для Docker:

   ```bash
   cp .env.docker.example .env.docker
   ```

2. Запустите:

   ```bash
   docker compose up --build
   ```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs


Остановить:

```bash
docker compose down # сохранить данные
docker compose down -v # удалить данные
```

## API

Все методы — GET. Параметр `ticker` обязателен, значения: `btc_usd`, `eth_usd`.

```bash
# health
curl "http://localhost:8000/api/v1/health"

# все цены по тикеру
curl "http://localhost:8000/api/v1/prices?ticker=btc_usd"

# последняя цена
curl "http://localhost:8000/api/v1/prices/latest?ticker=eth_usd"

# фильтр по UNIX timestamp (from_ts / to_ts необязательны)
curl "http://localhost:8000/api/v1/prices/filter?ticker=btc_usd&from_ts=1792003000&to_ts=1792005000"
```

## Локальный запуск

1. Поднять PostgreSQL и Redis:

   ```bash
   docker run --name deribit-pg \
     -e POSTGRES_USER=app -e POSTGRES_PASSWORD=app -e POSTGRES_DB=deribit \
     -p 5433:5432 -d postgres:16

   docker run --name deribit-redis -p 6379:6379 -d redis:7-alpine
   ```

2. Скопировать настройки для локального запуска.

   ```bash
   cp .env.example .env
   ```

3. Установить зависимости и накатить миграции:

   ```bash
   python -m venv .venv

   source .venv/bin/activate

   pip install -e ".[dev]"
   ```

4. Запустить три процесса в отдельных терминалах:

   ```bash
   uvicorn app.main:app --reload

   # Windows: добавь --pool=solo
   celery -A app.tasks.celery_app:celery_app worker --loglevel=info

   celery -A app.tasks.celery_app:celery_app beat --loglevel=info
   ```

## Тесты

```bash
pytest tests -v
```

Покрыто:

- `tests/test_clients/` — клиент Deribit (3 теста: успех, HTTP-ошибка, кривой ответ);
- `tests/test_repositories/` — репозиторий цен (1 тест: последняя цена по максимальному timestamp);
- `tests/test_services/` — сервис сбора цен (1 тест: сохранение по каждому тикеру).

Тесты репозитория используют SQLite in-memory (`aiosqlite`) — БД поднимать не нужно.
Общие константы и фикстуры — в `tests/constants.py` и `tests/conftest.py`.

## Переменные окружения

| Переменная               | По умолчанию                                       |
|--------------------------|----------------------------------------------------|
| `DATABASE_URL`           | `postgresql+asyncpg://app:app@db:5432/deribit`     |
| `CELERY_BROKER_URL`      | `redis://redis:6379/0`                             |
| `CELERY_RESULT_BACKEND`  | `redis://redis:6379/1`                             |
| `DERIBIT_BASE_URL`       | `https://www.deribit.com`                          |
| `DERIBIT_REQUEST_TIMEOUT`| `10`                                               |
| `FETCH_INTERVAL_SECONDS` | `60`                                               |
| `SUPPORTED_TICKERS`      | `["btc_usd","eth_usd"]`                            |
| `LOG_LEVEL`              | `INFO`                                             |

`SUPPORTED_TICKERS` задаётся JSON-массивом: `["btc_usd","eth_usd"]`.

## Архитектура

Слоистая, каждый слой знает только о нижнем:

- `clients` — Deribit (aiohttp).
- `repositories` — SQL-запросы.
- `services` — бизнес-логика.
- `db` — модели и сессия.
- `tasks` — Celery.
- `api` — роутеры и схемы.
- `core` — настройки, константы, логирование.

## Design decisions

**Celery + Redis.** Выносит фоновую работу из API в отдельный процесс;
beat отвечает за расписание, worker — за выполнение.

**aiohttp.** Клиент Deribit — тонкая обёртка над одним эндпоинтом, 
aiohttp даёт полный контроль над сессией и таймаутами.

**Decimal вместо float.** Цены нельзя хранить во `float` из-за ошибок
округления. В БД — `Numeric(20, 8)`, в Python — `Decimal`.

**Индекс `(ticker, timestamp)`.** Покрывает все три запроса API: «все по
тикеру», «последняя», «диапазон».

**Слои и DI без глобалов.** Настройки — через `get_settings()` (кэшированная
фабрика), движок и фабрика сессий — в `app.state` через lifespan.

**Commit в Celery-таске, а не в сервисе.** Граница транзакции в одном месте,
сервис и репозиторий переиспользуемы и легко тестируются.

**SQLite в тестах.** Быстро и без поднятия БД.
