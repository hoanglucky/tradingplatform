import asyncio
import json
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from typing import Any, Protocol, TypeAlias

import httpx
from pydantic import ValidationError
from websockets.asyncio.client import connect
from websockets.exceptions import WebSocketException

from app.core.config import settings
from app.core.logging import logger
from app.schemas.market_websocket import (
    MarketCandleUpdate,
    MarketSubscription,
    MarketWebSocketError,
)

MarketStreamEvent: TypeAlias = MarketCandleUpdate | MarketWebSocketError
StreamKey: TypeAlias = tuple[str, str]
OANDA_SYMBOL_MAP = {
    "XAUUSD": "XAU_USD",
    "SP500": "SPX500_USD",
    "US100": "NAS100_USD",
}
OANDA_TIMEFRAMES = {
    "1m": "M1",
    "5m": "M5",
    "15m": "M15",
    "1h": "H1",
    "4h": "H4",
    "1d": "D",
}


class MarketStreamError(RuntimeError):
    pass


class BinanceStreamError(MarketStreamError):
    pass


class OandaStreamError(MarketStreamError):
    pass


class MarketStreamSource(Protocol):
    def stream(
        self, subscription: MarketSubscription
    ) -> AsyncIterator[MarketCandleUpdate]: ...


def normalize_binance_kline(payload: object) -> MarketCandleUpdate:
    if not isinstance(payload, dict) or payload.get("e") != "kline":
        raise BinanceStreamError("Binance stream payload is not a kline event.")
    kline = payload.get("k")
    if not isinstance(kline, dict):
        raise BinanceStreamError("Binance kline payload is missing candle data.")

    try:
        symbol = kline["s"]
        timeframe = kline["i"]
        closed = kline["x"]
        if (
            not isinstance(symbol, str)
            or not isinstance(timeframe, str)
            or not isinstance(closed, bool)
        ):
            raise TypeError("Binance kline identity fields have invalid types.")
        return MarketCandleUpdate(
            symbol=symbol.upper(),
            timeframe=timeframe,
            timestamp=datetime.fromtimestamp(int(kline["t"]) / 1000, tz=timezone.utc),
            open=float(kline["o"]),
            high=float(kline["h"]),
            low=float(kline["l"]),
            close=float(kline["c"]),
            volume=float(kline["v"]),
            closed=closed,
        )
    except (KeyError, TypeError, ValueError, ValidationError) as error:
        raise BinanceStreamError(
            "Binance kline payload contains invalid candle data."
        ) from error


class BinanceMarketStreamSource:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or settings.binance_ws_base_url).rstrip("/")

    async def stream(
        self, subscription: MarketSubscription
    ) -> AsyncIterator[MarketCandleUpdate]:
        stream_name = f"{subscription.symbol.lower()}@kline_{subscription.timeframe}"
        async with connect(
            f"{self.base_url}/{stream_name}", open_timeout=10
        ) as websocket:
            async for raw_message in websocket:
                try:
                    payload = json.loads(raw_message)
                except (TypeError, json.JSONDecodeError) as error:
                    raise BinanceStreamError(
                        "Binance stream returned invalid JSON."
                    ) from error

                candle = normalize_binance_kline(payload)
                if (
                    candle.symbol != subscription.symbol
                    or candle.timeframe != subscription.timeframe
                ):
                    raise BinanceStreamError(
                        "Binance stream returned an unexpected subscription."
                    )
                yield candle


def market_source_for_symbol(symbol: str) -> str:
    return "oanda" if symbol.upper() in OANDA_SYMBOL_MAP else "binance"


def normalize_oanda_candle(
    payload: object, subscription: MarketSubscription
) -> MarketCandleUpdate:
    if not isinstance(payload, dict):
        raise OandaStreamError("Oanda response must be an object.")
    candles = payload.get("candles")
    if (
        not isinstance(candles, list)
        or not candles
        or not isinstance(candles[-1], dict)
    ):
        raise OandaStreamError("Oanda response is missing candle data.")
    candle: dict[str, Any] = candles[-1]
    mid = candle.get("mid")
    if not isinstance(mid, dict) or not isinstance(candle.get("complete"), bool):
        raise OandaStreamError("Oanda candle contains invalid price data.")

    try:
        return MarketCandleUpdate(
            symbol=subscription.symbol,
            timeframe=subscription.timeframe,
            timestamp=datetime.fromisoformat(
                str(candle["time"]).replace("Z", "+00:00")
            ),
            open=float(mid["o"]),
            high=float(mid["h"]),
            low=float(mid["l"]),
            close=float(mid["c"]),
            volume=float(candle["volume"]),
            closed=candle["complete"],
            source="oanda",
        )
    except (KeyError, TypeError, ValueError, ValidationError) as error:
        raise OandaStreamError("Oanda candle contains invalid OHLCV data.") from error


class OandaMarketStreamSource:
    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        poll_seconds: float | None = None,
    ) -> None:
        self.client = client
        self.poll_seconds = poll_seconds or settings.oanda_realtime_poll_seconds

    async def stream(
        self, subscription: MarketSubscription
    ) -> AsyncIterator[MarketCandleUpdate]:
        instrument = OANDA_SYMBOL_MAP.get(subscription.symbol)
        granularity = OANDA_TIMEFRAMES.get(subscription.timeframe)
        if instrument is None or granularity is None:
            raise OandaStreamError("Unsupported Oanda realtime subscription.")
        if not settings.oanda_api_token:
            raise OandaStreamError("OANDA_API_TOKEN is required for realtime candles.")

        close_client = self.client is None
        client = self.client or httpx.AsyncClient(base_url=self._base_url(), timeout=10)
        previous: MarketCandleUpdate | None = None
        try:
            while True:
                try:
                    response = await client.get(
                        f"/v3/instruments/{instrument}/candles",
                        params={"count": 1, "granularity": granularity, "price": "M"},
                        headers={
                            "Authorization": f"Bearer {settings.oanda_api_token}",
                            "Accept-Datetime-Format": "RFC3339",
                        },
                    )
                    response.raise_for_status()
                    update = normalize_oanda_candle(response.json(), subscription)
                except (httpx.HTTPError, ValueError) as error:
                    raise OandaStreamError(
                        f"Oanda realtime request failed: {error.__class__.__name__}"
                    ) from error

                if update != previous:
                    previous = update
                    yield update
                await asyncio.sleep(self.poll_seconds)
        finally:
            if close_client:
                await client.aclose()

    @staticmethod
    def _base_url() -> str:
        if settings.oanda_environment == "practice":
            return "https://api-fxpractice.oanda.com"
        if settings.oanda_environment == "live":
            return "https://api-fxtrade.oanda.com"
        raise OandaStreamError("OANDA_ENVIRONMENT must be practice or live.")


class RoutedMarketStreamSource:
    def __init__(
        self,
        binance: MarketStreamSource | None = None,
        oanda: MarketStreamSource | None = None,
    ) -> None:
        self.binance = binance or BinanceMarketStreamSource()
        self.oanda = oanda or OandaMarketStreamSource()

    async def stream(
        self, subscription: MarketSubscription
    ) -> AsyncIterator[MarketCandleUpdate]:
        source = (
            self.oanda
            if market_source_for_symbol(subscription.symbol) == "oanda"
            else self.binance
        )
        async for candle in source.stream(subscription):
            yield candle


class MarketStreamHub:
    def __init__(
        self,
        source: MarketStreamSource | None = None,
        reconnect_seconds: float | None = None,
        max_reconnect_seconds: float | None = None,
    ) -> None:
        self.source = source or RoutedMarketStreamSource()
        self.reconnect_seconds = (
            reconnect_seconds or settings.market_stream_reconnect_seconds
        )
        self.max_reconnect_seconds = (
            max_reconnect_seconds or settings.market_stream_max_reconnect_seconds
        )
        self._subscribers: dict[StreamKey, set[asyncio.Queue[MarketStreamEvent]]] = {}
        self._stream_tasks: dict[StreamKey, asyncio.Task[None]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(
        self, subscription: MarketSubscription
    ) -> asyncio.Queue[MarketStreamEvent]:
        key = self._key(subscription)
        queue: asyncio.Queue[MarketStreamEvent] = asyncio.Queue(maxsize=10)
        async with self._lock:
            self._subscribers.setdefault(key, set()).add(queue)
            task = self._stream_tasks.get(key)
            if task is None or task.done():
                self._stream_tasks[key] = asyncio.create_task(
                    self._run_stream(subscription)
                )
        return queue

    async def unsubscribe(
        self,
        subscription: MarketSubscription,
        queue: asyncio.Queue[MarketStreamEvent],
    ) -> None:
        key = self._key(subscription)
        task: asyncio.Task[None] | None = None
        async with self._lock:
            subscribers = self._subscribers.get(key)
            if subscribers is None:
                return
            subscribers.discard(queue)
            if not subscribers:
                self._subscribers.pop(key, None)
                task = self._stream_tasks.pop(key, None)
        if task is not None:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    async def _run_stream(self, subscription: MarketSubscription) -> None:
        key = self._key(subscription)
        delay = self.reconnect_seconds
        try:
            while await self._has_subscribers(key):
                try:
                    async for candle in self.source.stream(subscription):
                        await self._broadcast(key, candle)
                    raise MarketStreamError("Market stream ended unexpectedly.")
                except asyncio.CancelledError:
                    raise
                except (
                    MarketStreamError,
                    OSError,
                    WebSocketException,
                ) as error:
                    logger.warning(
                        "Market stream %s %s disconnected: %s; retrying in %.1fs",
                        subscription.symbol,
                        subscription.timeframe,
                        error,
                        delay,
                    )
                    await self._broadcast(
                        key,
                        MarketWebSocketError(
                            code="market_stream_reconnecting",
                            message="Market stream disconnected; reconnecting.",
                        ),
                    )
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, self.max_reconnect_seconds)
        finally:
            async with self._lock:
                current_task = self._stream_tasks.get(key)
                if current_task is asyncio.current_task():
                    self._stream_tasks.pop(key, None)

    async def _broadcast(self, key: StreamKey, event: MarketStreamEvent) -> None:
        async with self._lock:
            subscribers = tuple(self._subscribers.get(key, ()))
        for queue in subscribers:
            if queue.full():
                queue.get_nowait()
            queue.put_nowait(event)

    async def _has_subscribers(self, key: StreamKey) -> bool:
        async with self._lock:
            return bool(self._subscribers.get(key))

    @staticmethod
    def _key(subscription: MarketSubscription) -> StreamKey:
        return subscription.symbol, subscription.timeframe


market_stream_hub = MarketStreamHub()
