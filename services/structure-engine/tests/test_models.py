from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models import (
    Candle,
    MarketStructureState,
    StructureConfig,
    SwingDirection,
    SwingPoint,
)


def candle(**overrides: object) -> Candle:
    values = {
        "symbol": "XAUUSD",
        "timeframe": "5m",
        "timestamp": datetime(2026, 6, 30, 12, 0, tzinfo=UTC),
        "open": "3300",
        "high": "3305",
        "low": "3298",
        "close": "3302",
        "volume": "12",
    }
    values.update(overrides)
    return Candle.model_validate(values)


def swing(**overrides: object) -> SwingPoint:
    values = {
        "id": "XAUUSD:5m:2:HIGH",
        "symbol": "XAUUSD",
        "timeframe": "5m",
        "candle_index": 2,
        "timestamp": datetime(2026, 6, 30, 12, 10, tzinfo=UTC),
        "price": "3305",
        "direction": SwingDirection.HIGH,
    }
    values.update(overrides)
    return SwingPoint.model_validate(values)


def test_validates_and_freezes_candle_input() -> None:
    value = candle()

    assert value.close == Decimal("3302")
    with pytest.raises(ValidationError):
        value.close = Decimal("1")


@pytest.mark.parametrize(
    "overrides",
    [
        {"timestamp": datetime(2026, 6, 30, 12, 0)},
        {"high": "3301", "close": "3302"},
        {"low": "3303", "close": "3302"},
        {"volume": "-1"},
    ],
)
def test_rejects_invalid_candles(overrides: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        candle(**overrides)


def test_validates_swing_point_and_direction() -> None:
    point = swing(direction="LOW", price="3298")

    assert point.direction is SwingDirection.LOW
    assert point.confirmed is True


def test_rejects_invalid_structure_config() -> None:
    assert StructureConfig().min_distance == Decimal("0")
    with pytest.raises(ValidationError):
        StructureConfig(left_bars=0)
    with pytest.raises(ValidationError):
        StructureConfig(min_distance=Decimal("-0.1"))


def test_state_requires_matching_swings_inside_analyzed_range() -> None:
    state = MarketStructureState(
        symbol="XAUUSD",
        timeframe="5m",
        candle_count=3,
        swings=(swing(),),
        analyzed_at=datetime.now(UTC),
    )
    assert state.swings[0].candle_index == 2

    with pytest.raises(ValidationError, match="identity"):
        MarketStructureState(
            symbol="XAUUSD",
            timeframe="5m",
            candle_count=3,
            swings=(swing(symbol="BTCUSDT"),),
            analyzed_at=datetime.now(UTC),
        )
    with pytest.raises(ValidationError, match="analyzed candle"):
        MarketStructureState(
            symbol="XAUUSD",
            timeframe="5m",
            candle_count=2,
            swings=(swing(),),
            analyzed_at=datetime.now(UTC),
        )
