from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.schemas import Candle
from app.services.candle_storage import CandleStorageService
from app.storage.candles import SymbolNotFoundError


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def make_candle(timestamp: datetime, close: str = "100.00") -> Candle:
    return Candle(
        symbol="BTCUSDT",
        timeframe="1m",
        timestamp=timestamp,
        open=Decimal("99.00"),
        high=Decimal("101.00"),
        low=Decimal("98.00"),
        close=Decimal(close),
        volume=Decimal("10.00"),
    )


class FakeRepository:
    def __init__(
        self, candles: list[Candle] | None = None, symbol_exists: bool = True
    ) -> None:
        self.symbol_id = uuid.uuid4() if symbol_exists else None
        self.candles = {
            (candle.timeframe, candle.timestamp): candle for candle in candles or []
        }
        self.upserted: list[Candle] = []
        self.commits = 0

    async def get_symbol_id(
        self, symbol: str, exchange: str | None = None
    ) -> uuid.UUID | None:
        return self.symbol_id

    async def list_range(
        self,
        symbol_id: uuid.UUID,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        return sorted(
            [
                candle
                for (stored_timeframe, timestamp), candle in self.candles.items()
                if stored_timeframe == timeframe and start <= timestamp < end
            ],
            key=lambda candle: candle.timestamp,
        )

    async def upsert_many(self, symbol_id: uuid.UUID, candles: list[Candle]) -> None:
        self.upserted = candles
        self.candles.update(
            {(candle.timeframe, candle.timestamp): candle for candle in candles}
        )

    async def commit(self) -> None:
        self.commits += 1


class FakeProvider:
    def __init__(self, candles: list[Candle], exchange: str = "binance") -> None:
        self.candles = candles
        self.exchange = exchange
        self.calls = 0
        self.requested_timeframes: list[str] = []

    async def get_symbols(self):
        return []

    async def get_latest_price(self, symbol: str):
        raise NotImplementedError

    async def get_historical_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        self.calls += 1
        self.requested_timeframes.append(timeframe)
        return self.candles


@pytest.mark.anyio
async def test_returns_complete_cached_range_without_provider_call() -> None:
    start = datetime(2024, 6, 19, 8, 0, tzinfo=UTC)
    cached = [make_candle(start), make_candle(start + timedelta(minutes=1))]
    repository = FakeRepository(cached)
    provider = FakeProvider([])
    service = CandleStorageService(repository, provider)

    result = await service.get_candles(
        "BTCUSDT", "1m", start, start + timedelta(minutes=2)
    )

    assert result == cached
    assert provider.calls == 0
    assert repository.commits == 0


@pytest.mark.anyio
async def test_oanda_cache_allows_weekend_boundary_gap() -> None:
    start = datetime(2024, 6, 1, 0, 0, tzinfo=UTC)
    first_market_candle = start + timedelta(days=1, hours=22)
    end = first_market_candle + timedelta(minutes=2)
    cached = [
        make_candle(first_market_candle),
        make_candle(first_market_candle + timedelta(minutes=1)),
    ]
    repository = FakeRepository(cached)
    provider = FakeProvider([], exchange="oanda")
    service = CandleStorageService(repository, provider)

    result = await service.get_candles("XAUUSD", "1m", start, end)

    assert result == cached
    assert provider.calls == 0


@pytest.mark.anyio
async def test_oanda_stale_trailing_cache_fetches_current_range() -> None:
    start = datetime(2024, 6, 19, 8, 0, tzinfo=UTC)
    end = start + timedelta(minutes=10)
    cached = [make_candle(start), make_candle(start + timedelta(minutes=1))]
    fetched = [make_candle(start + timedelta(minutes=index)) for index in range(10)]
    repository = FakeRepository(cached)
    provider = FakeProvider(fetched, exchange="oanda")
    service = CandleStorageService(repository, provider)

    result = await service.get_candles("XAUUSD", "1m", start, end)

    assert provider.calls == 1
    assert len(result) == 10
    assert result[-1].timestamp == end - timedelta(minutes=1)


@pytest.mark.anyio
async def test_fetches_partial_range_and_deduplicates_before_upsert() -> None:
    start = datetime(2024, 6, 19, 8, 0, tzinfo=UTC)
    first = make_candle(start)
    second = make_candle(start + timedelta(minutes=1), close="102.00")
    duplicate_second = make_candle(start + timedelta(minutes=1), close="103.00")
    repository = FakeRepository([first])
    provider = FakeProvider([first, second, duplicate_second])
    service = CandleStorageService(repository, provider)

    result = await service.get_candles(
        "BTCUSDT", "1m", start, start + timedelta(minutes=2)
    )

    assert provider.calls == 1
    assert len(repository.upserted) == 2
    assert repository.commits == 1
    assert len(result) == 2
    assert result[-1].close == Decimal("103.00")


@pytest.mark.anyio
async def test_rejects_symbol_that_is_not_registered() -> None:
    repository = FakeRepository(symbol_exists=False)
    provider = FakeProvider([])
    service = CandleStorageService(repository, provider)

    with pytest.raises(SymbolNotFoundError):
        await service.get_candles(
            "UNKNOWN",
            "1m",
            datetime(2024, 6, 19, 8, 0, tzinfo=UTC),
            datetime(2024, 6, 19, 9, 0, tzinfo=UTC),
        )


@pytest.mark.anyio
async def test_aggregates_unsupported_oanda_timeframe_from_direct_base() -> None:
    start = datetime(2024, 6, 19, 8, 0, tzinfo=UTC)
    source = [make_candle(start + timedelta(minutes=index)) for index in range(6)]
    repository = FakeRepository()
    provider = FakeProvider(source, exchange="oanda")
    service = CandleStorageService(repository, provider)

    result = await service.get_candles("XAUUSD", "3m", start, start + timedelta(minutes=6))

    assert provider.requested_timeframes == ["1m"]
    assert [candle.timeframe for candle in result] == ["3m", "3m"]
    assert [candle.timestamp for candle in result] == [start, start + timedelta(minutes=3)]
    assert repository.commits == 2
