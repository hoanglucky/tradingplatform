import asyncio
from collections.abc import AsyncIterator

import pytest

from app.schemas.market_websocket import MarketCandleUpdate, MarketSubscription
from app.services.market_stream import (
    BinanceStreamError,
    MarketStreamHub,
    OandaStreamError,
    market_source_for_symbol,
    normalize_binance_kline,
    normalize_oanda_candle,
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def subscription() -> MarketSubscription:
    return MarketSubscription(type="subscribe", symbol="BTCUSDT", timeframe="1m")


def candle() -> MarketCandleUpdate:
    return MarketCandleUpdate(
        symbol="BTCUSDT",
        timeframe="1m",
        timestamp="2026-06-23T03:29:00Z",
        open=100.0,
        high=102.0,
        low=99.0,
        close=101.0,
        volume=12.5,
        closed=False,
    )


def test_normalize_binance_kline() -> None:
    result = normalize_binance_kline(
        {
            "e": "kline",
            "k": {
                "t": 1_750_648_140_000,
                "s": "BTCUSDT",
                "i": "1m",
                "o": "100.0",
                "h": "102.0",
                "l": "99.0",
                "c": "101.0",
                "v": "12.5",
                "x": False,
            },
        }
    )

    assert result.symbol == "BTCUSDT"
    assert result.timeframe == "1m"
    assert result.open == 100.0
    assert result.close == 101.0
    assert result.closed is False
    assert result.source == "binance"
    assert result.mock is False


def test_normalize_binance_kline_rejects_invalid_ohlc() -> None:
    with pytest.raises(BinanceStreamError, match="invalid candle data"):
        normalize_binance_kline(
            {
                "e": "kline",
                "k": {
                    "t": 1_750_648_140_000,
                    "s": "BTCUSDT",
                    "i": "1m",
                    "o": "100.0",
                    "h": "98.0",
                    "l": "99.0",
                    "c": "101.0",
                    "v": "12.5",
                    "x": False,
                },
            }
        )


def test_normalize_binance_kline_rejects_non_boolean_closed_state() -> None:
    with pytest.raises(BinanceStreamError, match="invalid candle data"):
        normalize_binance_kline(
            {
                "e": "kline",
                "k": {
                    "t": 1_750_648_140_000,
                    "s": "BTCUSDT",
                    "i": "1m",
                    "o": "100.0",
                    "h": "102.0",
                    "l": "99.0",
                    "c": "101.0",
                    "v": "12.5",
                    "x": "false",
                },
            }
        )


def test_normalize_oanda_current_candle() -> None:
    active_subscription = MarketSubscription(
        type="subscribe", symbol="XAUUSD", timeframe="1m"
    )
    result = normalize_oanda_candle(
        {
            "candles": [
                {
                    "complete": False,
                    "volume": 42,
                    "time": "2026-06-29T08:31:00Z",
                    "mid": {
                        "o": "2325.10",
                        "h": "2326.40",
                        "l": "2324.80",
                        "c": "2326.05",
                    },
                }
            ]
        },
        active_subscription,
    )

    assert result.symbol == "XAUUSD"
    assert result.close == 2326.05
    assert result.closed is False
    assert result.source == "oanda"


@pytest.mark.parametrize("timeframe", ["30m", "2h"])
def test_oanda_extended_realtime_timeframes(timeframe: str) -> None:
    subscription = MarketSubscription(
        type="subscribe", symbol="XAUUSD", timeframe=timeframe
    )

    assert subscription.timeframe == timeframe


def test_normalize_oanda_candle_rejects_invalid_data() -> None:
    active_subscription = MarketSubscription(
        type="subscribe", symbol="SP500", timeframe="5m"
    )
    with pytest.raises(OandaStreamError, match="invalid OHLCV"):
        normalize_oanda_candle(
            {
                "candles": [
                    {
                        "complete": False,
                        "volume": 1,
                        "time": "2026-06-29T08:30:00Z",
                        "mid": {"o": "10", "h": "9", "l": "8", "c": "11"},
                    }
                ]
            },
            active_subscription,
        )


@pytest.mark.parametrize("symbol", ["XAUUSD", "SP500", "US100"])
def test_market_source_routes_oanda_symbols(symbol: str) -> None:
    assert market_source_for_symbol(symbol) == "oanda"


def test_market_source_defaults_to_binance() -> None:
    assert market_source_for_symbol("BTCUSDT") == "binance"


class ControlledSource:
    def __init__(self) -> None:
        self.calls = 0
        self.release = asyncio.Event()
        self.stop = asyncio.Event()

    async def stream(
        self, active_subscription: MarketSubscription
    ) -> AsyncIterator[MarketCandleUpdate]:
        self.calls += 1
        await self.release.wait()
        yield candle()
        await self.stop.wait()


@pytest.mark.anyio
async def test_hub_shares_stream_and_broadcasts_to_subscribers() -> None:
    source = ControlledSource()
    hub = MarketStreamHub(
        source=source, reconnect_seconds=0.01, max_reconnect_seconds=0.02
    )
    active_subscription = subscription()

    first_queue = await hub.subscribe(active_subscription)
    second_queue = await hub.subscribe(active_subscription)
    source.release.set()

    first_event, second_event = await asyncio.gather(
        asyncio.wait_for(first_queue.get(), timeout=1),
        asyncio.wait_for(second_queue.get(), timeout=1),
    )

    assert first_event == candle()
    assert second_event == candle()
    assert source.calls == 1

    await hub.unsubscribe(active_subscription, first_queue)
    await hub.unsubscribe(active_subscription, second_queue)


class ReconnectingSource:
    def __init__(self) -> None:
        self.calls = 0
        self.stop = asyncio.Event()

    async def stream(
        self, active_subscription: MarketSubscription
    ) -> AsyncIterator[MarketCandleUpdate]:
        self.calls += 1
        if self.calls == 1:
            raise BinanceStreamError("connection lost")
        yield candle()
        await self.stop.wait()


@pytest.mark.anyio
async def test_hub_reports_disconnect_and_reconnects() -> None:
    source = ReconnectingSource()
    hub = MarketStreamHub(
        source=source, reconnect_seconds=0.01, max_reconnect_seconds=0.02
    )
    active_subscription = subscription()
    queue = await hub.subscribe(active_subscription)

    reconnecting = await asyncio.wait_for(queue.get(), timeout=1)
    update = await asyncio.wait_for(queue.get(), timeout=1)

    assert reconnecting.type == "error"
    assert reconnecting.code == "market_stream_reconnecting"
    assert update == candle()
    assert source.calls == 2

    await hub.unsubscribe(active_subscription, queue)
