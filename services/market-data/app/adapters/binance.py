from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import httpx

from app.schemas import Candle, LatestPrice, MarketSymbol

BINANCE_BASE_URL = "https://api.binance.com"
BINANCE_INTERVALS = {
    "1s",
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
    "6h",
    "8h",
    "12h",
    "1d",
    "3d",
    "1w",
    "1M",
}


class BinanceAdapterError(RuntimeError):
    pass


class BinanceValidationError(ValueError):
    pass


class BinancePublicMarketDataProvider:
    exchange = "binance"

    def __init__(
        self,
        *,
        base_url: str = BINANCE_BASE_URL,
        client: httpx.AsyncClient | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = client
        self._timeout = timeout

    async def get_symbols(self) -> list[MarketSymbol]:
        payload = await self._get_json("/api/v3/exchangeInfo")
        symbols = payload.get("symbols")
        if not isinstance(symbols, list):
            raise BinanceAdapterError(
                "Binance exchangeInfo response is missing symbols."
            )

        normalized: list[MarketSymbol] = []
        for item in symbols:
            if not isinstance(item, dict) or item.get("status") != "TRADING":
                continue
            normalized.append(
                MarketSymbol(
                    exchange="binance",
                    symbol=str(item["symbol"]),
                    base_asset=str(item["baseAsset"]),
                    quote_asset=str(item["quoteAsset"]),
                    is_active=True,
                )
            )
        return normalized

    async def get_historical_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        self._validate_symbol(symbol)
        self._validate_timeframe(timeframe)
        self._validate_time_range(start, end)

        cursor = self._to_milliseconds(start)
        end_milliseconds = self._to_milliseconds(end)
        normalized: dict[datetime, Candle] = {}
        while cursor < end_milliseconds:
            rows = await self._get_json(
                "/api/v3/klines",
                params={
                    "symbol": symbol.upper(),
                    "interval": timeframe,
                    "startTime": cursor,
                    "endTime": end_milliseconds - 1,
                    "limit": 1000,
                },
            )
            if not isinstance(rows, list):
                raise BinanceAdapterError("Binance klines response must be a list.")
            if not rows:
                break

            for row in rows:
                parsed = self._parse_kline(symbol.upper(), timeframe, row)
                normalized[parsed.timestamp] = parsed
            if len(rows) < 1000:
                break
            last_open_time = rows[-1][0] if isinstance(rows[-1], list) else None
            if not isinstance(last_open_time, int) or last_open_time < cursor:
                raise BinanceAdapterError("Binance kline pagination did not advance.")
            cursor = last_open_time + 1

        return sorted(normalized.values(), key=lambda candle: candle.timestamp)

    async def get_latest_price(self, symbol: str) -> LatestPrice:
        self._validate_symbol(symbol)
        payload = await self._get_json(
            "/api/v3/ticker/price", params={"symbol": symbol.upper()}
        )
        if not isinstance(payload, dict) or "price" not in payload:
            raise BinanceAdapterError("Binance ticker price response is invalid.")

        return LatestPrice(
            symbol=symbol.upper(),
            timestamp=datetime.now(tz=UTC),
            price=Decimal(str(payload["price"])),
        )

    async def _get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        close_client = self._client is None
        client = self._client or httpx.AsyncClient(
            base_url=self.base_url, timeout=self._timeout
        )
        try:
            response = await client.get(path, params=params)
        except httpx.HTTPError as exc:
            raise BinanceAdapterError(
                f"Binance request failed: {exc.__class__.__name__}"
            ) from exc
        finally:
            if close_client:
                await client.aclose()

        if response.status_code >= 400:
            detail = self._extract_error_detail(response)
            raise BinanceAdapterError(
                f"Binance API error {response.status_code}: {detail}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise BinanceAdapterError("Binance response was not valid JSON.") from exc

    @staticmethod
    def _parse_kline(symbol: str, timeframe: str, row: Any) -> Candle:
        if not isinstance(row, list) or len(row) < 6:
            raise BinanceAdapterError("Binance kline row is invalid.")

        return Candle(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=datetime.fromtimestamp(int(row[0]) / 1000, tz=UTC),
            open=Decimal(str(row[1])),
            high=Decimal(str(row[2])),
            low=Decimal(str(row[3])),
            close=Decimal(str(row[4])),
            volume=Decimal(str(row[5])),
        )

    @staticmethod
    def _validate_symbol(symbol: str) -> None:
        if not symbol or not symbol.strip():
            raise BinanceValidationError("symbol is required")

    @staticmethod
    def _validate_timeframe(timeframe: str) -> None:
        if timeframe not in BINANCE_INTERVALS:
            raise BinanceValidationError(f"unsupported Binance interval: {timeframe}")

    @staticmethod
    def _validate_time_range(start: datetime, end: datetime) -> None:
        if start.tzinfo is None or start.utcoffset() is None:
            raise BinanceValidationError("start must be timezone-aware")
        if end.tzinfo is None or end.utcoffset() is None:
            raise BinanceValidationError("end must be timezone-aware")
        if start >= end:
            raise BinanceValidationError("start must be before end")

    @staticmethod
    def _to_milliseconds(value: datetime) -> int:
        return int(value.timestamp() * 1000)

    @staticmethod
    def _extract_error_detail(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return response.text

        if isinstance(payload, dict) and "msg" in payload:
            return str(payload["msg"])
        return str(payload)
