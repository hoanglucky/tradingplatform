from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Protocol

from app.providers import MarketDataProvider
from app.schemas import Candle
from app.storage.candles import SymbolNotFoundError

TIMEFRAME_DURATION = {
    "1m": timedelta(minutes=1),
    "3m": timedelta(minutes=3),
    "5m": timedelta(minutes=5),
    "15m": timedelta(minutes=15),
    "30m": timedelta(minutes=30),
    "1h": timedelta(hours=1),
    "2h": timedelta(hours=2),
    "4h": timedelta(hours=4),
    "6h": timedelta(hours=6),
    "8h": timedelta(hours=8),
    "12h": timedelta(hours=12),
    "1d": timedelta(days=1),
    "3d": timedelta(days=3),
    "1w": timedelta(weeks=1),
}


class CandleRepositoryProtocol(Protocol):
    async def get_symbol_id(
        self, symbol: str, exchange: str | None = None
    ) -> uuid.UUID | None: ...

    async def list_range(
        self,
        symbol_id: uuid.UUID,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]: ...

    async def upsert_many(
        self, symbol_id: uuid.UUID, candles: list[Candle]
    ) -> None: ...

    async def commit(self) -> None: ...


class CandleStorageService:
    def __init__(
        self, repository: CandleRepositoryProtocol, provider: MarketDataProvider
    ) -> None:
        self.repository = repository
        self.provider = provider

    async def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        exchange = getattr(self.provider, "exchange", None)
        symbol_id = await self.repository.get_symbol_id(symbol, exchange)
        if symbol_id is None:
            raise SymbolNotFoundError(f"Symbol {symbol.upper()} is not registered.")

        cached = await self.repository.list_range(
            symbol_id, symbol, timeframe, start, end
        )
        if self._cache_covers_range(cached, timeframe, start, end, exchange):
            return cached

        fetched = await self.provider.get_historical_candles(
            symbol, timeframe, start, end
        )
        unique = list({candle.timestamp: candle for candle in fetched}.values())
        unique.sort(key=lambda candle: candle.timestamp)
        await self.repository.upsert_many(symbol_id, unique)
        await self.repository.commit()

        return await self.repository.list_range(
            symbol_id, symbol, timeframe, start, end
        )

    @staticmethod
    def _cache_covers_range(
        candles: list[Candle],
        timeframe: str,
        start: datetime,
        end: datetime,
        exchange: str | None = None,
    ) -> bool:
        duration = TIMEFRAME_DURATION.get(timeframe)
        if not candles or duration is None:
            return False
        leading_tolerance = timedelta(days=3) if exchange == "oanda" else duration
        return (
            candles[0].timestamp <= start + leading_tolerance
            and candles[-1].timestamp + duration >= end
        )
