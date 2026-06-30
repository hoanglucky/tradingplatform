from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

TimeframeUnit = Literal["m", "h", "d"]
TIMEFRAME_PATTERN = re.compile(r"^([1-9][0-9]*)([mhd])$")
UNIT_MILLISECONDS: dict[TimeframeUnit, int] = {
    "m": 60_000,
    "h": 3_600_000,
    "d": 86_400_000,
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
    normalized = value.strip().lower()
    match = TIMEFRAME_PATTERN.fullmatch(normalized)
    if match is None:
        raise TimeframeValidationError(
            "Timeframe must be a positive integer followed by m, h, or d."
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
