from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

TimeframeUnit = Literal["m", "h", "d", "w", "M"]
TIMEFRAME_PATTERN = re.compile(r"^([1-9][0-9]*)([mhdw])$", re.IGNORECASE)
UNIT_MILLISECONDS: dict[TimeframeUnit, int] = {
    "m": 60_000,
    "h": 3_600_000,
    "d": 86_400_000,
    "w": 604_800_000,
    "M": 2_678_400_000,
}
MAX_TIMEFRAME_MILLISECONDS = 31 * UNIT_MILLISECONDS["d"]


class TimeframeValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ParsedTimeframe:
    value: str
    amount: int
    unit: TimeframeUnit
    duration_milliseconds: int


def parse_timeframe(value: str) -> ParsedTimeframe:
    if not isinstance(value, str):
        raise TimeframeValidationError("Timeframe must be a string.")
    candidate = value.strip()
    if candidate == "1M":
        return ParsedTimeframe(
            value="1M",
            amount=1,
            unit="M",
            duration_milliseconds=UNIT_MILLISECONDS["M"],
        )
    normalized = candidate.lower()
    match = TIMEFRAME_PATTERN.fullmatch(normalized)
    if match is None:
        raise TimeframeValidationError(
            "Timeframe must be a positive integer followed by m, h, d, or w; 1M means one month."
        )

    amount = int(match.group(1))
    unit = match.group(2)
    duration_milliseconds = amount * UNIT_MILLISECONDS[unit]
    if duration_milliseconds > MAX_TIMEFRAME_MILLISECONDS:
        raise TimeframeValidationError("Timeframe duration cannot exceed 31 days.")
    return ParsedTimeframe(
        value=f"{amount}{unit}",
        amount=amount,
        unit=unit,
        duration_milliseconds=duration_milliseconds,
    )


def normalize_timeframe(value: str) -> str:
    return parse_timeframe(value).value


def timeframe_duration_milliseconds(value: str) -> int:
    return parse_timeframe(value).duration_milliseconds
