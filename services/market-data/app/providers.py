from __future__ import annotations

from datetime import datetime
from typing import Protocol

from app.schemas import Candle, LatestPrice, MarketSymbol


class MarketDataProvider(Protocol):
    async def get_symbols(self) -> list[MarketSymbol]:
        """Return symbols supported by this provider."""

    async def get_historical_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        """Return normalized candles ordered by timestamp."""

    async def get_latest_price(self, symbol: str) -> LatestPrice:
        """Return the latest normalized price for one symbol."""
