import asyncio
import threading

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.api.routes import market_websocket as market_websocket_routes
from app.main import app
from app.schemas.market_websocket import MarketCandleUpdate, MarketSubscription
from app.services.market_stream import MarketStreamEvent


client = TestClient(app)


def make_candle(symbol: str = "BTCUSDT", timeframe: str = "1m") -> MarketCandleUpdate:
    return MarketCandleUpdate(
        symbol=symbol,
        timeframe=timeframe,
        timestamp="2026-06-23T03:29:00Z",
        open=100.0,
        high=102.0,
        low=99.0,
        close=101.0,
        volume=12.5,
        closed=False,
    )


class FakeMarketStreamHub:
    def __init__(self, emit_candles: bool = False) -> None:
        self.emit_candles = emit_candles
        self.subscriptions: list[MarketSubscription] = []
        self.unsubscriptions: list[MarketSubscription] = []
        self.unsubscription_condition = threading.Condition()

    async def subscribe(
        self, subscription: MarketSubscription
    ) -> asyncio.Queue[MarketStreamEvent]:
        self.subscriptions.append(subscription)
        queue: asyncio.Queue[MarketStreamEvent] = asyncio.Queue()
        if self.emit_candles:
            queue.put_nowait(make_candle(subscription.symbol, subscription.timeframe))
        return queue

    async def unsubscribe(
        self,
        subscription: MarketSubscription,
        queue: asyncio.Queue[MarketStreamEvent],
    ) -> None:
        with self.unsubscription_condition:
            self.unsubscriptions.append(subscription)
            self.unsubscription_condition.notify_all()

    def wait_for_unsubscriptions(self, count: int) -> bool:
        with self.unsubscription_condition:
            return self.unsubscription_condition.wait_for(
                lambda: len(self.unsubscriptions) >= count,
                timeout=1,
            )


def test_market_websocket_subscribes_and_receives_binance_candle(monkeypatch) -> None:
    hub = FakeMarketStreamHub(emit_candles=True)
    monkeypatch.setattr(market_websocket_routes, "market_stream_hub", hub)

    with client.websocket_connect("/ws/market") as websocket:
        websocket.send_json(
            {"type": "subscribe", "symbol": "btcusdt", "timeframe": "1m"}
        )

        acknowledgement = websocket.receive_json()
        assert acknowledgement == {
            "type": "subscribed",
            "symbol": "BTCUSDT",
            "timeframe": "1m",
            "source": "binance",
            "mock": False,
        }

        candle = websocket.receive_json()
        assert candle["type"] == "candle"
        assert candle["symbol"] == "BTCUSDT"
        assert candle["timeframe"] == "1m"
        assert candle["source"] == "binance"
        assert candle["mock"] is False
        assert candle["low"] <= candle["open"] <= candle["high"]
        assert candle["low"] <= candle["close"] <= candle["high"]
        assert candle["volume"] > 0

    assert hub.wait_for_unsubscriptions(1)
    assert hub.unsubscriptions[0].symbol == "BTCUSDT"


def test_market_websocket_acknowledges_oanda_source(monkeypatch) -> None:
    hub = FakeMarketStreamHub()
    monkeypatch.setattr(market_websocket_routes, "market_stream_hub", hub)

    with client.websocket_connect("/ws/market") as websocket:
        websocket.send_json(
            {"type": "subscribe", "symbol": "XAUUSD", "timeframe": "1m"}
        )
        acknowledgement = websocket.receive_json()

        assert acknowledgement["source"] == "oanda"
        assert acknowledgement["symbol"] == "XAUUSD"

    assert hub.wait_for_unsubscriptions(1)


def test_market_websocket_rejects_invalid_subscription(monkeypatch) -> None:
    hub = FakeMarketStreamHub()
    monkeypatch.setattr(market_websocket_routes, "market_stream_hub", hub)

    with client.websocket_connect("/ws/market") as websocket:
        websocket.send_json(
            {"type": "subscribe", "symbol": "BTCUSDT", "timeframe": "2m"}
        )

        response = websocket.receive_json()
        assert response == {
            "type": "error",
            "code": "invalid_subscription",
            "message": "Expected a subscribe message with a valid symbol and timeframe.",
        }

    assert hub.subscriptions == []


def test_market_websocket_replaces_active_subscription(monkeypatch) -> None:
    hub = FakeMarketStreamHub()
    monkeypatch.setattr(market_websocket_routes, "market_stream_hub", hub)

    with client.websocket_connect("/ws/market") as websocket:
        websocket.send_json(
            {"type": "subscribe", "symbol": "BTCUSDT", "timeframe": "1m"}
        )
        assert websocket.receive_json()["symbol"] == "BTCUSDT"

        websocket.send_json(
            {"type": "subscribe", "symbol": "ETHUSDT", "timeframe": "5m"}
        )
        acknowledgement = websocket.receive_json()

        assert acknowledgement["type"] == "subscribed"
        assert acknowledgement["symbol"] == "ETHUSDT"
        assert acknowledgement["timeframe"] == "5m"

    assert [item.symbol for item in hub.subscriptions] == ["BTCUSDT", "ETHUSDT"]
    assert hub.wait_for_unsubscriptions(2)
    assert [item.symbol for item in hub.unsubscriptions] == ["BTCUSDT", "ETHUSDT"]


def test_market_websocket_does_not_duplicate_same_subscription(monkeypatch) -> None:
    hub = FakeMarketStreamHub()
    monkeypatch.setattr(market_websocket_routes, "market_stream_hub", hub)

    with client.websocket_connect("/ws/market") as websocket:
        subscription = {"type": "subscribe", "symbol": "BTCUSDT", "timeframe": "1m"}
        websocket.send_json(subscription)
        assert websocket.receive_json()["type"] == "subscribed"

        websocket.send_json(subscription)
        assert websocket.receive_json()["type"] == "subscribed"

    assert len(hub.subscriptions) == 1
    assert hub.wait_for_unsubscriptions(1)


def test_market_websocket_heartbeat_accepts_matching_pong(monkeypatch) -> None:
    monkeypatch.setattr(
        market_websocket_routes.settings, "market_ws_heartbeat_seconds", 0.01
    )
    monkeypatch.setattr(
        market_websocket_routes.settings, "market_ws_stale_seconds", 0.2
    )

    with client.websocket_connect("/ws/market") as websocket:
        first_heartbeat = websocket.receive_json()
        assert first_heartbeat["type"] == "heartbeat"
        websocket.send_json({"type": "pong", "id": first_heartbeat["id"]})

        second_heartbeat = websocket.receive_json()
        assert second_heartbeat["type"] == "heartbeat"
        assert second_heartbeat["id"] > first_heartbeat["id"]


def test_market_websocket_closes_stale_client(monkeypatch) -> None:
    monkeypatch.setattr(
        market_websocket_routes.settings, "market_ws_heartbeat_seconds", 0.01
    )
    monkeypatch.setattr(
        market_websocket_routes.settings, "market_ws_stale_seconds", 0.025
    )

    with pytest.raises(WebSocketDisconnect) as disconnect:
        with client.websocket_connect("/ws/market") as websocket:
            while True:
                websocket.receive_json()

    assert disconnect.value.code == 1001
