from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from app.candle_aggregator import CandleAggregationError, aggregate_candles
from app.schemas import Candle


def make_candles(count: int = 15) -> list[Candle]:
    start = datetime(1970, 1, 1, tzinfo=UTC)
    return [
        Candle(
            symbol="BTCUSDT",
            timeframe="1m",
            timestamp=start + timedelta(minutes=index),
            open=Decimal(100 + index),
            high=Decimal(101 + index),
            low=Decimal(99 + index),
            close=Decimal("100.5") + index,
            volume=Decimal(index + 1),
        )
        for index in range(count)
    ]


@pytest.mark.parametrize(
    ("target_timeframe", "expected_count"),
    [("5m", 3), ("6m", 3), ("7m", 3), ("15m", 1)],
)
def test_aggregates_one_minute_candles_into_fixed_buckets(
    target_timeframe: str, expected_count: int
) -> None:
    result = aggregate_candles(make_candles(), target_timeframe)

    assert len(result) == expected_count
    assert all(candle.timeframe == target_timeframe for candle in result)
    assert result == sorted(result, key=lambda candle: candle.timestamp)


def test_calculates_ohlcv_from_the_bucket() -> None:
    result = aggregate_candles(make_candles(5), "5m")

    assert len(result) == 1
    assert result[0].timestamp == datetime(1970, 1, 1, tzinfo=UTC)
    assert result[0].open == Decimal("100")
    assert result[0].high == Decimal("105")
    assert result[0].low == Decimal("99")
    assert result[0].close == Decimal("104.5")
    assert result[0].volume == Decimal("15")
    assert result[0].complete is True
    assert result[0].missing_source_count == 0


def test_marks_closed_bucket_with_missing_source_candles() -> None:
    candles = [candle for index, candle in enumerate(make_candles(5)) if index != 2]

    result = aggregate_candles(
        candles,
        "5m",
        as_of=datetime(1970, 1, 1, 0, 5, tzinfo=UTC),
    )

    assert result[0].source_count == 4
    assert result[0].expected_source_count == 5
    assert result[0].missing_source_count == 1
    assert result[0].complete is False


def test_duplicate_timestamp_uses_latest_value_once() -> None:
    candles = make_candles(5)
    replacement = candles[2].model_copy(
        update={
            "high": Decimal("150"),
            "close": Decimal("149"),
            "volume": Decimal("20"),
        }
    )

    result = aggregate_candles([*candles, replacement], "5m")

    assert result[0].high == Decimal("150")
    assert result[0].volume == Decimal("32")
    assert result[0].source_count == 5


def test_groups_timezone_aware_input_into_utc_buckets() -> None:
    local_timezone = timezone(timedelta(hours=7))
    candles = make_candles(5)
    shifted = [
        candle.model_copy(
            update={"timestamp": candle.timestamp.astimezone(local_timezone)}
        )
        for candle in reversed(candles)
    ]

    result = aggregate_candles(shifted, "5m")

    assert result[0].timestamp == datetime(1970, 1, 1, tzinfo=UTC)
    assert result[0].timestamp.tzinfo is UTC
    assert result[0].open == Decimal("100")
    assert result[0].close == Decimal("104.5")


def test_groups_across_utc_day_boundary() -> None:
    candles = [
        candle.model_copy(
            update={"timestamp": datetime(2026, 6, 29, 23, 58, tzinfo=UTC) + timedelta(minutes=index)}
        )
        for index, candle in enumerate(make_candles(5))
    ]

    result = aggregate_candles(candles, "5m")

    assert [candle.timestamp for candle in result] == [
        datetime(2026, 6, 29, 23, 55, tzinfo=UTC),
        datetime(2026, 6, 30, 0, 0, tzinfo=UTC),
    ]


def test_dst_input_still_uses_fixed_utc_buckets() -> None:
    new_york = ZoneInfo("America/New_York")
    utc_candles = [
        candle.model_copy(
            update={"timestamp": datetime(2026, 3, 8, 6, 58, tzinfo=UTC) + timedelta(minutes=index)}
        )
        for index, candle in enumerate(make_candles(5))
    ]
    local_candles = [
        candle.model_copy(update={"timestamp": candle.timestamp.astimezone(new_york)})
        for candle in utc_candles
    ]

    result = aggregate_candles(local_candles, "5m")

    assert [candle.timestamp for candle in result] == [
        datetime(2026, 3, 8, 6, 55, tzinfo=UTC),
        datetime(2026, 3, 8, 7, 0, tzinfo=UTC),
    ]


def test_empty_input_returns_empty_output() -> None:
    assert aggregate_candles([], "5m") == []


def test_normalizes_source_and_target_timeframes() -> None:
    candles = [
        candle.model_copy(update={"timeframe": " 1m "}) for candle in make_candles(5)
    ]

    result = aggregate_candles(candles, " 5M ")

    assert len(result) == 1
    assert result[0].timeframe == "5m"


def test_week_buckets_start_on_monday_utc() -> None:
    candles = [
        Candle(
            symbol="BTCUSDT",
            timeframe="1d",
            timestamp=datetime(2026, 6, 30, tzinfo=UTC),
            open=Decimal("100"),
            high=Decimal("101"),
            low=Decimal("99"),
            close=Decimal("100"),
            volume=Decimal("1"),
        )
    ]

    result = aggregate_candles(candles, "2w")

    assert result[0].timestamp.weekday() == 0


def test_marks_completed_and_active_buckets() -> None:
    as_of = datetime(1970, 1, 1, 0, 7, tzinfo=UTC)

    result = aggregate_candles(make_candles(10), "5m", as_of=as_of)

    assert [(candle.closed, candle.partial) for candle in result] == [
        (True, False),
        (False, True),
    ]


def test_bucket_is_closed_at_its_exact_end_time() -> None:
    result = aggregate_candles(
        make_candles(5),
        "5m",
        as_of=datetime(1970, 1, 1, 0, 5, tzinfo=UTC),
    )

    assert result[0].closed is True
    assert result[0].partial is False


def test_backtest_mode_excludes_partial_bucket() -> None:
    result = aggregate_candles(
        make_candles(10),
        "5m",
        as_of=datetime(1970, 1, 1, 0, 7, tzinfo=UTC),
        include_partial=False,
    )

    assert len(result) == 1
    assert result[0].timestamp == datetime(1970, 1, 1, tzinfo=UTC)
    assert result[0].closed is True


def test_rejects_naive_as_of_time() -> None:
    with pytest.raises(CandleAggregationError, match="timezone-aware"):
        aggregate_candles(
            make_candles(5),
            "5m",
            as_of=datetime(1970, 1, 1, 0, 5),
        )


def test_rejects_target_smaller_than_source() -> None:
    candles = [candle.model_copy(update={"timeframe": "5m"}) for candle in make_candles()]

    with pytest.raises(CandleAggregationError, match="cannot be smaller"):
        aggregate_candles(candles, "1m")


def test_rejects_target_that_is_not_source_multiple() -> None:
    candles = [candle.model_copy(update={"timeframe": "2m"}) for candle in make_candles()]

    with pytest.raises(CandleAggregationError, match="must be a multiple"):
        aggregate_candles(candles, "5m")


def test_rejects_mixed_symbols_and_timeframes() -> None:
    candles = make_candles(3)
    with pytest.raises(CandleAggregationError, match="same symbol"):
        aggregate_candles(
            [*candles, candles[-1].model_copy(update={"symbol": "ETHUSDT"})],
            "5m",
        )

    with pytest.raises(CandleAggregationError, match="same source timeframe"):
        aggregate_candles(
            [*candles, candles[-1].model_copy(update={"timeframe": "5m"})],
            "5m",
        )
