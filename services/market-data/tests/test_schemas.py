from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas import Candle, LatestPrice, MarketSymbol


def test_candle_schema_accepts_valid_ohlcv_payload() -> None:
    candle = Candle(
        symbol="BTCUSDT",
        timeframe="1m",
        timestamp=datetime(2026, 6, 19, 7, 0, tzinfo=UTC),
        open=Decimal("65000.10"),
        high=Decimal("65100.25"),
        low=Decimal("64950.00"),
        close=Decimal("65050.50"),
        volume=Decimal("123.456"),
    )

    assert candle.symbol == "BTCUSDT"
    assert candle.timestamp.tzinfo is not None
    assert candle.volume == Decimal("123.456")


def test_candle_schema_rejects_naive_timestamp() -> None:
    with pytest.raises(ValidationError):
        Candle(
            symbol="BTCUSDT",
            timeframe="1m",
            timestamp=datetime(2026, 6, 19, 7, 0),
            open=Decimal("65000.10"),
            high=Decimal("65100.25"),
            low=Decimal("64950.00"),
            close=Decimal("65050.50"),
            volume=Decimal("123.456"),
        )


def test_candle_schema_rejects_non_positive_price() -> None:
    with pytest.raises(ValidationError):
        Candle(
            symbol="BTCUSDT",
            timeframe="1m",
            timestamp=datetime(2026, 6, 19, 7, 0, tzinfo=UTC),
            open=Decimal("0"),
            high=Decimal("65100.25"),
            low=Decimal("64950.00"),
            close=Decimal("65050.50"),
            volume=Decimal("123.456"),
        )


def test_market_symbol_schema_accepts_default_catalog_shape() -> None:
    symbol = MarketSymbol(
        exchange="binance",
        symbol="ETHUSDT",
        base_asset="ETH",
        quote_asset="USDT",
    )

    assert symbol.is_active is True


def test_latest_price_schema_requires_positive_price() -> None:
    with pytest.raises(ValidationError):
        LatestPrice(
            symbol="BTCUSDT",
            timestamp=datetime(2026, 6, 19, 7, 0, tzinfo=UTC),
            price=Decimal("-1"),
        )
