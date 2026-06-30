from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from urllib.parse import parse_qs

import httpx
import pytest

from app.adapters.oanda import (
    OandaAdapterError,
    OandaConfigurationError,
    OandaMarketDataProvider,
    OandaValidationError,
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_fetches_oanda_candles_as_internal_schema() -> None:
    seen_params: dict[str, list[str]] = {}
    seen_auth = ""
    seen_path = ""

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_params, seen_auth, seen_path
        seen_path = request.url.path
        seen_params = parse_qs(request.url.query.decode())
        seen_auth = request.headers["Authorization"]
        return httpx.Response(
            200,
            json={
                "instrument": "XAU_USD",
                "granularity": "M1",
                "candles": [
                    {
                        "complete": True,
                        "volume": 42,
                        "time": "2024-06-19T08:00:00.000000000Z",
                        "mid": {
                            "o": "2310.10",
                            "h": "2312.20",
                            "l": "2309.90",
                            "c": "2311.50",
                        },
                    },
                    {
                        "complete": False,
                        "volume": 1,
                        "time": "2024-06-19T08:01:00.000000000Z",
                        "mid": {
                            "o": "1",
                            "h": "1",
                            "l": "1",
                            "c": "1",
                        },
                    },
                ],
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://api-fxpractice.oanda.com",
    ) as client:
        provider = OandaMarketDataProvider(api_token="token", client=client)
        candles = await provider.get_historical_candles(
            "XAUUSD",
            "1m",
            datetime(2024, 6, 19, 8, 0, tzinfo=UTC),
            datetime(2024, 6, 19, 9, 0, tzinfo=UTC),
        )

    assert seen_path == "/v3/instruments/XAU_USD/candles"
    assert seen_auth == "Bearer token"
    assert seen_params["granularity"] == ["M1"]
    assert seen_params["price"] == ["M"]
    assert candles[0].symbol == "XAUUSD"
    assert candles[0].timeframe == "1m"
    assert candles[0].timestamp == datetime(2024, 6, 19, 8, 0, tzinfo=UTC)
    assert candles[0].close == Decimal("2311.50")
    assert len(candles) == 1


@pytest.mark.anyio
async def test_paginates_oanda_ranges_larger_than_provider_limit() -> None:
    requested_ranges: list[tuple[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        params = parse_qs(request.url.query.decode())
        requested_ranges.append((params["from"][0], params["to"][0]))
        candle_time = params["from"][0]
        return httpx.Response(
            200,
            json={
                "candles": [
                    {
                        "complete": True,
                        "volume": 1,
                        "time": candle_time,
                        "mid": {"o": "10", "h": "11", "l": "9", "c": "10.5"},
                    }
                ]
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://api-fxpractice.oanda.com",
    ) as client:
        provider = OandaMarketDataProvider(api_token="token", client=client)
        candles = await provider.get_historical_candles(
            "XAUUSD",
            "1m",
            datetime(2024, 5, 1, tzinfo=UTC),
            datetime(2024, 6, 1, tzinfo=UTC),
        )

    assert len(requested_ranges) > 1
    assert all(
        requested_ranges[index - 1][1] == requested_ranges[index][0]
        for index in range(1, len(requested_ranges))
    )
    assert len(candles) == len(requested_ranges)
    assert candles == sorted(candles, key=lambda candle: candle.timestamp)


@pytest.mark.anyio
async def test_fetches_oanda_account_instruments_when_account_id_is_configured() -> (
    None
):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v3/accounts/abc/instruments"
        return httpx.Response(
            200,
            json={
                "instruments": [
                    {"name": "XAU_USD", "type": "METAL"},
                    {"name": "SPX500_USD", "type": "CFD"},
                    {"name": "EUR_USD", "type": "CURRENCY"},
                ]
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://api-fxpractice.oanda.com",
    ) as client:
        provider = OandaMarketDataProvider(
            api_token="token", account_id="abc", client=client
        )
        symbols = await provider.get_symbols()

    assert [symbol.symbol for symbol in symbols] == ["XAUUSD", "SP500", "EURUSD"]


@pytest.mark.anyio
async def test_oanda_get_symbols_returns_default_symbols_without_account_id() -> None:
    provider = OandaMarketDataProvider(api_token="token", account_id="")

    symbols = await provider.get_symbols()

    assert [symbol.symbol for symbol in symbols] == ["XAUUSD", "SP500", "US100"]


@pytest.mark.anyio
async def test_oanda_requires_api_token_for_http_requests() -> None:
    provider = OandaMarketDataProvider(api_token="")

    with pytest.raises(OandaConfigurationError):
        await provider.get_historical_candles(
            "XAUUSD",
            "1m",
            datetime(2024, 6, 19, 8, 0, tzinfo=UTC),
            datetime(2024, 6, 19, 9, 0, tzinfo=UTC),
        )


@pytest.mark.anyio
async def test_oanda_rejects_invalid_timeframe_before_request() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _request: httpx.Response(500))
    ) as client:
        provider = OandaMarketDataProvider(api_token="token", client=client)
        with pytest.raises(OandaValidationError):
            await provider.get_historical_candles(
                "XAUUSD",
                "2m",
                datetime(2024, 6, 19, 8, 0, tzinfo=UTC),
                datetime(2024, 6, 19, 9, 0, tzinfo=UTC),
            )


@pytest.mark.anyio
async def test_oanda_supports_two_hour_candles_directly() -> None:
    seen_granularity = ""

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_granularity
        seen_granularity = parse_qs(request.url.query.decode())["granularity"][0]
        return httpx.Response(200, json={"candles": []})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://api-fxpractice.oanda.com",
    ) as client:
        provider = OandaMarketDataProvider(api_token="token", client=client)
        candles = await provider.get_historical_candles(
            "XAUUSD",
            "2h",
            datetime(2024, 6, 19, 8, 0, tzinfo=UTC),
            datetime(2024, 6, 19, 12, 0, tzinfo=UTC),
        )

    assert seen_granularity == "H2"
    assert candles == []


@pytest.mark.anyio
async def test_oanda_wraps_api_errors() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"errorMessage": "Insufficient authorization"})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://api-fxpractice.oanda.com",
    ) as client:
        provider = OandaMarketDataProvider(api_token="bad-token", client=client)
        with pytest.raises(OandaAdapterError, match="Insufficient authorization"):
            await provider.get_historical_candles(
                "XAUUSD",
                "1m",
                datetime(2024, 6, 19, 8, 0, tzinfo=UTC),
                datetime(2024, 6, 19, 9, 0, tzinfo=UTC),
            )
