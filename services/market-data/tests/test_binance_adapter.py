from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from urllib.parse import parse_qs

import httpx
import pytest

from app.adapters.binance import (
    BinanceAdapterError,
    BinancePublicMarketDataProvider,
    BinanceValidationError,
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_fetches_historical_klines_as_internal_candles() -> None:
    seen_params: dict[str, list[str]] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_params
        seen_params = parse_qs(request.url.query.decode())
        return httpx.Response(
            200,
            json=[
                [
                    1718784000000,
                    "65000.10",
                    "65100.25",
                    "64950.00",
                    "65050.50",
                    "123.456",
                    1718784059999,
                    "0",
                    10,
                    "0",
                    "0",
                    "0",
                ]
            ],
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.binance.com"
    ) as client:
        provider = BinancePublicMarketDataProvider(client=client)
        candles = await provider.get_historical_candles(
            "btcusdt",
            "1m",
            datetime(2024, 6, 19, 8, 0, tzinfo=UTC),
            datetime(2024, 6, 19, 9, 0, tzinfo=UTC),
        )

    assert seen_params["symbol"] == ["BTCUSDT"]
    assert seen_params["interval"] == ["1m"]
    assert candles[0].symbol == "BTCUSDT"
    assert candles[0].timeframe == "1m"
    assert candles[0].timestamp == datetime(2024, 6, 19, 8, 0, tzinfo=UTC)
    assert candles[0].open == Decimal("65000.10")
    assert candles[0].volume == Decimal("123.456")


@pytest.mark.anyio
async def test_paginates_binance_ranges_larger_than_provider_limit() -> None:
    requested_starts: list[int] = []
    first_open = 1718784000000

    def row(open_time: int) -> list[object]:
        return [
            open_time,
            "100",
            "102",
            "99",
            "101",
            "1",
            open_time + 59_999,
        ]

    def handler(request: httpx.Request) -> httpx.Response:
        params = parse_qs(request.url.query.decode())
        requested_starts.append(int(params["startTime"][0]))
        if len(requested_starts) == 1:
            return httpx.Response(
                200,
                json=[row(first_open + index * 60_000) for index in range(1000)],
            )
        return httpx.Response(200, json=[row(first_open + 1000 * 60_000)])

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.binance.com"
    ) as client:
        provider = BinancePublicMarketDataProvider(client=client)
        candles = await provider.get_historical_candles(
            "BTCUSDT",
            "1m",
            datetime.fromtimestamp(first_open / 1000, tz=UTC),
            datetime.fromtimestamp((first_open + 1001 * 60_000) / 1000, tz=UTC),
        )

    assert len(requested_starts) == 2
    assert requested_starts[1] == first_open + 999 * 60_000 + 1
    assert len(candles) == 1001
    assert candles[0].timestamp < candles[-1].timestamp


@pytest.mark.anyio
async def test_fetches_trading_symbols_from_exchange_info() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "symbols": [
                    {
                        "symbol": "BTCUSDT",
                        "status": "TRADING",
                        "baseAsset": "BTC",
                        "quoteAsset": "USDT",
                    },
                    {
                        "symbol": "OLDUSDT",
                        "status": "BREAK",
                        "baseAsset": "OLD",
                        "quoteAsset": "USDT",
                    },
                ]
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.binance.com"
    ) as client:
        provider = BinancePublicMarketDataProvider(client=client)
        symbols = await provider.get_symbols()

    assert [symbol.symbol for symbol in symbols] == ["BTCUSDT"]
    assert symbols[0].exchange == "binance"


@pytest.mark.anyio
async def test_fetches_latest_price() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"symbol": "BTCUSDT", "price": "65050.50"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.binance.com"
    ) as client:
        provider = BinancePublicMarketDataProvider(client=client)
        latest = await provider.get_latest_price("btcusdt")

    assert latest.symbol == "BTCUSDT"
    assert latest.price == Decimal("65050.50")


@pytest.mark.anyio
async def test_rejects_invalid_timeframe_before_request() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _request: httpx.Response(500))
    ) as client:
        provider = BinancePublicMarketDataProvider(client=client)
        with pytest.raises(BinanceValidationError):
            await provider.get_historical_candles(
                "BTCUSDT",
                "10minutes",
                datetime(2024, 6, 19, 8, 0, tzinfo=UTC),
                datetime(2024, 6, 19, 9, 0, tzinfo=UTC),
            )


@pytest.mark.anyio
async def test_rejects_invalid_time_range_before_request() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _request: httpx.Response(500))
    ) as client:
        provider = BinancePublicMarketDataProvider(client=client)
        with pytest.raises(BinanceValidationError):
            await provider.get_historical_candles(
                "BTCUSDT",
                "1m",
                datetime(2024, 6, 19, 9, 0, tzinfo=UTC),
                datetime(2024, 6, 19, 8, 0, tzinfo=UTC),
            )


@pytest.mark.anyio
async def test_raises_adapter_error_for_binance_api_errors() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"code": -1121, "msg": "Invalid symbol."})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.binance.com"
    ) as client:
        provider = BinancePublicMarketDataProvider(client=client)
        with pytest.raises(BinanceAdapterError, match="Invalid symbol"):
            await provider.get_historical_candles(
                "BADUSDT",
                "1m",
                datetime(2024, 6, 19, 8, 0, tzinfo=UTC),
                datetime(2024, 6, 19, 9, 0, tzinfo=UTC),
            )
