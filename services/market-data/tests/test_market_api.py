from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from app.adapters.binance import BinanceAdapterError, BinanceValidationError
from app.adapters.oanda import OandaConfigurationError, OandaMarketDataProvider
from app.api.routes.market import get_candle_storage_service, get_market_data_provider
from app.main import app
from app.schemas import Candle, CandleQueryMetadata, CandleQueryResult
from app.storage.candles import SymbolNotFoundError

client = TestClient(app)


class StubStorageService:
    async def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        return [
            Candle(
                symbol=symbol.upper(),
                timeframe=timeframe,
                timestamp=start,
                open=Decimal("65000.10"),
                high=Decimal("65100.25"),
                low=Decimal("64950.00"),
                close=Decimal("65050.50"),
                volume=Decimal("123.456"),
            )
        ]

    async def get_candles_with_metadata(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> CandleQueryResult:
        return CandleQueryResult(
            candles=await self.get_candles(symbol, timeframe, start, end),
            metadata=CandleQueryMetadata(
                source_provider="oanda" if symbol.upper() == "XAUUSD" else "binance",
                source_market_type="cfd_fx" if symbol.upper() == "XAUUSD" else "spot_crypto",
                aggregation_used=timeframe == "45m",
                base_timeframe="15m" if timeframe == "45m" else None,
                cache_hit=False,
                missing_ranges_fetched=1,
            ),
        )


class ErrorStorageService(StubStorageService):
    def __init__(self, error: Exception) -> None:
        self.error = error

    async def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        raise self.error

    async def get_candles_with_metadata(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> CandleQueryResult:
        raise self.error


def test_market_candles_returns_internal_candle_format_for_btcusdt() -> None:
    app.dependency_overrides[get_candle_storage_service] = lambda: StubStorageService()
    try:
        response = client.get(
            "/market/candles",
            params={
                "symbol": "BTCUSDT",
                "timeframe": "1m",
                "start": datetime(2024, 6, 19, 8, 0, tzinfo=UTC).isoformat(),
                "end": datetime(2024, 6, 19, 9, 0, tzinfo=UTC).isoformat(),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    candle = payload["candles"][0]
    assert candle["symbol"] == "BTCUSDT"
    assert candle["timeframe"] == "1m"
    assert candle["timestamp"] == "2024-06-19T08:00:00Z"
    assert candle["close"] == "65050.50"
    assert payload["metadata"]["source_provider"] == "binance"
    assert payload["metadata"]["aggregation_used"] is False


def test_market_candles_requires_all_query_params() -> None:
    response = client.get("/market/candles", params={"symbol": "BTCUSDT"})

    assert response.status_code == 422


def test_market_candles_accepts_and_normalizes_custom_timeframe() -> None:
    app.dependency_overrides[get_candle_storage_service] = lambda: StubStorageService()
    try:
        response = client.get(
            "/market/candles",
            params={
                "symbol": "XAUUSD",
                "timeframe": "45M",
                "start": datetime(2024, 6, 19, 8, 0, tzinfo=UTC).isoformat(),
                "end": datetime(2024, 6, 19, 9, 0, tzinfo=UTC).isoformat(),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["candles"][0]["timeframe"] == "45m"
    assert payload["metadata"]["aggregation_used"] is True
    assert payload["metadata"]["base_timeframe"] == "15m"


def test_market_candles_rejects_invalid_custom_timeframe() -> None:
    app.dependency_overrides[get_candle_storage_service] = lambda: StubStorageService()
    try:
        response = client.get(
            "/market/candles",
            params={
                "symbol": "XAUUSD",
                "timeframe": "0m",
                "start": datetime(2024, 6, 19, 8, 0, tzinfo=UTC).isoformat(),
                "end": datetime(2024, 6, 19, 9, 0, tzinfo=UTC).isoformat(),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400


def test_market_candles_maps_validation_errors_to_bad_request() -> None:
    app.dependency_overrides[get_candle_storage_service] = lambda: ErrorStorageService(
        BinanceValidationError("unsupported Binance interval: 2m")
    )
    try:
        response = client.get(
            "/market/candles",
            params={
                "symbol": "BTCUSDT",
                "timeframe": "2m",
                "start": "2024-06-19T08:00:00Z",
                "end": "2024-06-19T09:00:00Z",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "unsupported Binance interval: 2m"


def test_market_candles_maps_provider_errors_to_bad_gateway() -> None:
    app.dependency_overrides[get_candle_storage_service] = lambda: ErrorStorageService(
        BinanceAdapterError("upstream unavailable")
    )
    try:
        response = client.get(
            "/market/candles",
            params={
                "symbol": "BTCUSDT",
                "timeframe": "1m",
                "start": "2024-06-19T08:00:00Z",
                "end": "2024-06-19T09:00:00Z",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json()["detail"] == "Market data provider request failed."


def test_market_candles_maps_missing_oanda_token_to_service_unavailable() -> None:
    app.dependency_overrides[get_candle_storage_service] = lambda: ErrorStorageService(
        OandaConfigurationError("OANDA_API_TOKEN is required for Oanda market data.")
    )
    try:
        response = client.get(
            "/market/candles",
            params={
                "symbol": "XAUUSD",
                "timeframe": "1m",
                "start": "2024-06-19T08:00:00Z",
                "end": "2024-06-19T09:00:00Z",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert "OANDA_API_TOKEN" in response.json()["detail"]


def test_market_candles_maps_unknown_symbol_to_not_found() -> None:
    app.dependency_overrides[get_candle_storage_service] = lambda: ErrorStorageService(
        SymbolNotFoundError("Symbol UNKNOWN is not registered.")
    )
    try:
        response = client.get(
            "/market/candles",
            params={
                "symbol": "UNKNOWN",
                "timeframe": "1m",
                "start": "2024-06-19T08:00:00Z",
                "end": "2024-06-19T09:00:00Z",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404


def test_provider_routing_uses_oanda_for_xauusd() -> None:
    provider = get_market_data_provider("XAUUSD")

    assert isinstance(provider, OandaMarketDataProvider)
