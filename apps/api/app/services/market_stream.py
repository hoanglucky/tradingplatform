import asyncio
import json
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from typing import Protocol, TypeAlias

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


class BinanceStreamError(RuntimeError):
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


class MarketStreamHub:
    def __init__(
        self,
        source: MarketStreamSource | None = None,
        reconnect_seconds: float | None = None,
        max_reconnect_seconds: float | None = None,
    ) -> None:
        self.source = source or BinanceMarketStreamSource()
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
                    raise BinanceStreamError("Binance stream ended unexpectedly.")
                except asyncio.CancelledError:
                    raise
                except (
                    BinanceStreamError,
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
