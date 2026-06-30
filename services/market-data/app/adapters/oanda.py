from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

import httpx

from app.config import settings
from app.schemas import Candle, LatestPrice, MarketSymbol

OANDA_PRACTICE_BASE_URL = "https://api-fxpractice.oanda.com"
OANDA_LIVE_BASE_URL = "https://api-fxtrade.oanda.com"
OANDA_TIMEFRAMES = {
    "1m": "M1",
    "5m": "M5",
    "15m": "M15",
    "30m": "M30",
    "1h": "H1",
    "2h": "H2",
    "4h": "H4",
    "1d": "D",
    "1w": "W",
}
OANDA_TIMEFRAME_DURATION = {
    "1m": timedelta(minutes=1),
    "5m": timedelta(minutes=5),
    "15m": timedelta(minutes=15),
    "30m": timedelta(minutes=30),
    "1h": timedelta(hours=1),
    "2h": timedelta(hours=2),
    "4h": timedelta(hours=4),
    "1d": timedelta(days=1),
    "1w": timedelta(weeks=1),
}
OANDA_MAX_CANDLES_PER_REQUEST = 5000
OANDA_SYMBOL_MAP = {
    "XAUUSD": "XAU_USD",
    "SP500": "SPX500_USD",
    "US100": "NAS100_USD",
}


class OandaAdapterError(RuntimeError):
    pass


class OandaConfigurationError(OandaAdapterError):
    pass


class OandaValidationError(ValueError):
    pass


class OandaMarketDataProvider:
    exchange = "oanda"

    def __init__(
        self,
        *,
        api_token: str | None = None,
        account_id: str | None = None,
        environment: str | None = None,
        base_url: str | None = None,
        client: httpx.AsyncClient | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.api_token = (
            api_token if api_token is not None else settings.oanda_api_token
        )
        self.account_id = (
            account_id if account_id is not None else settings.oanda_account_id
        )
        self.environment = (
            environment if environment is not None else settings.oanda_environment
        )
        self.base_url = (
            base_url or self._base_url_for_environment(self.environment)
        ).rstrip("/")
        self._client = client
        self._timeout = timeout

    async def get_symbols(self) -> list[MarketSymbol]:
        if not self.account_id:
            return [
                MarketSymbol(
                    exchange="oanda",
                    symbol="XAUUSD",
                    base_asset="XAU",
                    quote_asset="USD",
                ),
                MarketSymbol(
                    exchange="oanda",
                    symbol="SP500",
                    base_asset="SP500",
                    quote_asset="USD",
                ),
                MarketSymbol(
                    exchange="oanda",
                    symbol="US100",
                    base_asset="US100",
                    quote_asset="USD",
                ),
            ]

        payload = await self._get_json(f"/v3/accounts/{self.account_id}/instruments")
        instruments = payload.get("instruments")
        if not isinstance(instruments, list):
            raise OandaAdapterError(
                "Oanda instruments response is missing instruments."
            )

        symbols: list[MarketSymbol] = []
        for instrument in instruments:
            if not isinstance(instrument, dict) or instrument.get("type") not in {
                "CFD",
                "METAL",
                "CURRENCY",
            }:
                continue
            name = str(instrument["name"])
            display_name = self._to_internal_symbol(name)
            symbols.append(
                MarketSymbol(
                    exchange="oanda",
                    symbol=display_name,
                    base_asset=display_name[:-3],
                    quote_asset=display_name[-3:],
                    is_active=True,
                )
            )
        return symbols

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

        instrument = self._to_oanda_instrument(symbol)
        chunk_duration = OANDA_TIMEFRAME_DURATION[timeframe] * (
            OANDA_MAX_CANDLES_PER_REQUEST - 1
        )
        cursor = start
        normalized: dict[datetime, Candle] = {}
        while cursor < end:
            chunk_end = min(cursor + chunk_duration, end)
            payload = await self._get_json(
                f"/v3/instruments/{instrument}/candles",
                params={
                    "from": self._to_oanda_time(cursor),
                    "to": self._to_oanda_time(chunk_end),
                    "granularity": OANDA_TIMEFRAMES[timeframe],
                    "price": "M",
                },
            )
            candles = payload.get("candles")
            if not isinstance(candles, list):
                raise OandaAdapterError("Oanda candles response is missing candles.")
            for candle in candles:
                if candle.get("complete"):
                    parsed = self._parse_candle(symbol.upper(), timeframe, candle)
                    normalized[parsed.timestamp] = parsed
            cursor = chunk_end

        return sorted(normalized.values(), key=lambda candle: candle.timestamp)

    async def get_latest_price(self, symbol: str) -> LatestPrice:
        candles = await self.get_historical_candles(
            symbol,
            "1m",
            start=datetime.now().astimezone().replace(second=0, microsecond=0),
            end=datetime.now().astimezone(),
        )
        if not candles:
            raise OandaAdapterError("Oanda returned no latest candle for price.")
        latest = candles[-1]
        return LatestPrice(
            symbol=latest.symbol, timestamp=latest.timestamp, price=latest.close
        )

    async def _get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        if not self.api_token:
            raise OandaConfigurationError(
                "OANDA_API_TOKEN is required for Oanda market data."
            )

        close_client = self._client is None
        client = self._client or httpx.AsyncClient(
            base_url=self.base_url, timeout=self._timeout
        )
        try:
            response = await client.get(
                path,
                params=params,
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Accept-Datetime-Format": "RFC3339",
                },
            )
        except httpx.HTTPError as exc:
            raise OandaAdapterError(
                f"Oanda request failed: {exc.__class__.__name__}"
            ) from exc
        finally:
            if close_client:
                await client.aclose()

        if response.status_code >= 400:
            detail = self._extract_error_detail(response)
            raise OandaAdapterError(f"Oanda API error {response.status_code}: {detail}")

        try:
            return response.json()
        except ValueError as exc:
            raise OandaAdapterError("Oanda response was not valid JSON.") from exc

    @staticmethod
    def _parse_candle(symbol: str, timeframe: str, payload: dict[str, Any]) -> Candle:
        mid = payload.get("mid")
        if not isinstance(mid, dict):
            raise OandaAdapterError("Oanda candle is missing mid prices.")

        return Candle(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=datetime.fromisoformat(
                str(payload["time"]).replace("Z", "+00:00")
            ),
            open=Decimal(str(mid["o"])),
            high=Decimal(str(mid["h"])),
            low=Decimal(str(mid["l"])),
            close=Decimal(str(mid["c"])),
            volume=Decimal(str(payload["volume"])),
        )

    @staticmethod
    def _validate_symbol(symbol: str) -> None:
        if not symbol or not symbol.strip():
            raise OandaValidationError("symbol is required")

    @staticmethod
    def _validate_timeframe(timeframe: str) -> None:
        if timeframe not in OANDA_TIMEFRAMES:
            raise OandaValidationError(f"unsupported Oanda timeframe: {timeframe}")

    @staticmethod
    def _validate_time_range(start: datetime, end: datetime) -> None:
        if start.tzinfo is None or start.utcoffset() is None:
            raise OandaValidationError("start must be timezone-aware")
        if end.tzinfo is None or end.utcoffset() is None:
            raise OandaValidationError("end must be timezone-aware")
        if start >= end:
            raise OandaValidationError("start must be before end")

    @staticmethod
    def _to_oanda_time(value: datetime) -> str:
        return value.isoformat().replace("+00:00", "Z")

    @staticmethod
    def _to_oanda_instrument(symbol: str) -> str:
        normalized = symbol.upper().replace("/", "").replace("-", "").replace("_", "")
        if normalized in OANDA_SYMBOL_MAP:
            return OANDA_SYMBOL_MAP[normalized]
        if len(normalized) == 6:
            return f"{normalized[:3]}_{normalized[3:]}"
        raise OandaValidationError(f"unsupported Oanda symbol: {symbol}")

    @staticmethod
    def _to_internal_symbol(instrument: str) -> str:
        reverse_map = {value: key for key, value in OANDA_SYMBOL_MAP.items()}
        if instrument in reverse_map:
            return reverse_map[instrument]
        return instrument.replace("_", "")

    @staticmethod
    def _base_url_for_environment(environment: str) -> str:
        if environment == "practice":
            return OANDA_PRACTICE_BASE_URL
        if environment == "live":
            return OANDA_LIVE_BASE_URL
        raise OandaValidationError("OANDA_ENVIRONMENT must be practice or live")

    @staticmethod
    def _extract_error_detail(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return response.text

        if isinstance(payload, dict):
            return str(payload.get("errorMessage") or payload.get("message") or payload)
        return str(payload)
