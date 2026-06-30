from __future__ import annotations

import pytest

from app.timeframes import (
    TimeframeValidationError,
    normalize_timeframe,
    parse_timeframe,
    timeframe_duration_milliseconds,
)


@pytest.mark.parametrize(
    ("value", "expected_milliseconds"),
    [
        ("1m", 60_000),
        ("5m", 300_000),
        ("6m", 360_000),
        ("7m", 420_000),
        ("15m", 900_000),
        ("30m", 1_800_000),
        ("1h", 3_600_000),
        ("2h", 7_200_000),
        ("4h", 14_400_000),
        ("1d", 86_400_000),
    ],
)
def test_parses_supported_timeframe_units(
    value: str, expected_milliseconds: int
) -> None:
    parsed = parse_timeframe(value)

    assert parsed.value == value
    assert parsed.duration_milliseconds == expected_milliseconds
    assert timeframe_duration_milliseconds(value) == expected_milliseconds


def test_normalizes_whitespace_and_unit_case() -> None:
    parsed = parse_timeframe("  45M ")

    assert parsed.value == "45m"
    assert parsed.amount == 45
    assert parsed.unit == "m"
    assert normalize_timeframe(" 3H ") == "3h"


@pytest.mark.parametrize(
    "value",
    ["", "0m", "-5m", "abc", "1x", "1.5h", "m5", "32d"],
)
def test_rejects_invalid_or_unsafe_timeframes(value: str) -> None:
    with pytest.raises(TimeframeValidationError):
        parse_timeframe(value)


def test_rejects_non_string_values() -> None:
    with pytest.raises(TimeframeValidationError, match="must be a string"):
        parse_timeframe(5)  # type: ignore[arg-type]
