from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Protocol

from app.providers import MarketDataProvider
from app.candle_aggregator import aggregate_candles
from app.provider_capabilities import get_provider_capability, provider_supports_direct_timeframe
from app.schemas import Candle, CandleQueryMetadata, CandleQueryResult
from app.storage.candles import SymbolNotFoundError
from app.timeframes import parse_timeframe

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
    "2w": timedelta(weeks=2),
    "1M": timedelta(days=31),
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
        return (await self.get_candles_with_metadata(symbol, timeframe, start, end)).candles

    async def get_candles_with_metadata(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> CandleQueryResult:
        exchange = getattr(self.provider, "exchange", None)
        capability = get_provider_capability(str(exchange))
        target = parse_timeframe(timeframe)
        timeframe = target.value
        direct = provider_supports_direct_timeframe(str(exchange), timeframe)
        base_timeframe = None if direct else self._aggregation_base_timeframe(str(exchange), timeframe)
        symbol_id = await self.repository.get_symbol_id(symbol, exchange)
        if symbol_id is None:
            raise SymbolNotFoundError(f"Symbol {symbol.upper()} is not registered.")

        cached = await self.repository.list_range(
            symbol_id, symbol, timeframe, start, end
        )
        if self._cache_covers_range(cached, timeframe, start, end, exchange):
            return CandleQueryResult(
                candles=cached,
                metadata=CandleQueryMetadata(
                    source_provider=capability.provider,
                    source_market_type=capability.market_type,
                    aggregation_used=not direct,
                    base_timeframe=base_timeframe,
                    cache_hit=True,
                    missing_ranges_fetched=0,
                    partial_candle_count=sum(candle.partial for candle in cached),
                    incomplete_candle_count=sum(not candle.complete for candle in cached),
                    missing_source_candle_count=sum(
                        candle.missing_source_count or 0 for candle in cached
                    ),
                ),
            )

        missing_ranges_fetched = 0
        if direct:
            fetched = await self.provider.get_historical_candles(
                symbol, timeframe, start, end
            )
            missing_ranges_fetched = 1
        else:
            assert base_timeframe is not None
            base_result = await self.get_candles_with_metadata(
                symbol, base_timeframe, start, end
            )
            base_candles = base_result.candles
            missing_ranges_fetched = base_result.metadata.missing_ranges_fetched
            fetched = [
                Candle.model_validate(candle.model_dump(exclude={"closed"}))
                for candle in aggregate_candles(base_candles, timeframe)
            ]
        unique = list({candle.timestamp: candle for candle in fetched}.values())
        unique.sort(key=lambda candle: candle.timestamp)
        await self.repository.upsert_many(symbol_id, unique)
        await self.repository.commit()

        result = await self.repository.list_range(
            symbol_id, symbol, timeframe, start, end
        )
        return CandleQueryResult(
            candles=result,
            metadata=CandleQueryMetadata(
                source_provider=capability.provider,
                source_market_type=capability.market_type,
                aggregation_used=not direct,
                base_timeframe=base_timeframe,
                cache_hit=False,
                missing_ranges_fetched=missing_ranges_fetched,
                partial_candle_count=sum(candle.partial for candle in result),
                incomplete_candle_count=sum(not candle.complete for candle in result),
                missing_source_candle_count=sum(
                    candle.missing_source_count or 0 for candle in result
                ),
            ),
        )

    @staticmethod
    def _aggregation_base_timeframe(exchange: str, target_timeframe: str) -> str:
        target = parse_timeframe(target_timeframe)
        candidates = (
            ("1d", "4h", "2h", "1h", "30m", "15m", "5m", "3m", "1m")
            if exchange == "binance"
            else ("1d", "4h", "2h", "1h", "30m", "15m", "5m", "1m")
        )
        for candidate in candidates:
            parsed = parse_timeframe(candidate)
            if (
                parsed.duration_milliseconds <= target.duration_milliseconds
                and target.duration_milliseconds % parsed.duration_milliseconds == 0
                and provider_supports_direct_timeframe(exchange, candidate)
            ):
                return candidate
        raise ValueError(f"No aggregation base timeframe is available for {target_timeframe}.")

    @staticmethod
    def _cache_covers_range(
        candles: list[Candle],
        timeframe: str,
        start: datetime,
        end: datetime,
        exchange: str | None = None,
    ) -> bool:
        duration = TIMEFRAME_DURATION.get(timeframe)
        if duration is None:
            try:
                duration = timedelta(
                    milliseconds=parse_timeframe(timeframe).duration_milliseconds
                )
            except ValueError:
                return False
        if not candles or duration is None:
            return False
        if candles[-1].partial or not candles[-1].complete:
            return False
        leading_tolerance = timedelta(days=3) if exchange == "oanda" else duration
        return (
            candles[0].timestamp <= start + leading_tolerance
            and candles[-1].timestamp + duration >= end
        )
