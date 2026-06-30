from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Timeframe = Literal["1m", "5m", "15m", "1h", "4h", "1d"]
Theme = Literal["light", "dark", "system"]
INDICATOR_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,31}$")
ReviewTimeframe = str
WindowCount = Literal[1, 2, 4, 8]


class MultiTimeframeWindow(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: str = Field(min_length=1, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")
    timeframe: ReviewTimeframe = Field(min_length=2, max_length=16)
    enabled: bool
    reviewChecked: bool

    @field_validator("timeframe")
    @classmethod
    def validate_timeframe(cls, value: str) -> str:
        candidate = value.strip()
        if candidate == "1M":
            return candidate
        match = re.fullmatch(r"([1-9][0-9]*)([mhdw])", candidate.lower())
        if match is None:
            raise ValueError("Invalid chart timeframe.")
        amount = int(match.group(1))
        unit = match.group(2)
        days = amount * {"m": 1 / 1440, "h": 1 / 24, "d": 1, "w": 7}[unit]
        if days > 31:
            raise ValueError("Chart timeframe cannot exceed one month.")
        return f"{amount}{unit}"


class MultiTimeframeLayout(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    symbol: str = Field(min_length=2, max_length=40, pattern=r"^[A-Z0-9_]+$")
    window_count: WindowCount = Field(alias="windowCount")
    windows: list[MultiTimeframeWindow] = Field(min_length=1, max_length=8)

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_symbol(cls, value: object) -> object:
        return value.strip().upper() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_windows(self) -> "MultiTimeframeLayout":
        ids = [window.id for window in self.windows]
        if len(set(ids)) != len(ids):
            raise ValueError("Multi-timeframe window ids must be unique.")
        if len(self.windows) < self.window_count:
            raise ValueError("Layout must contain at least windowCount windows.")
        enabled_count = sum(window.enabled for window in self.windows)
        if enabled_count != self.window_count:
            raise ValueError("Enabled window count must match windowCount.")
        return self


class UserSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    default_symbol: str
    default_timeframe: Timeframe
    selected_indicators: list[str]
    theme: Theme
    timezone: str
    multi_timeframe_layout: MultiTimeframeLayout | None
    created_at: datetime
    updated_at: datetime


class UserSettingsPatch(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    default_symbol: str | None = Field(
        default=None, min_length=2, max_length=40, pattern=r"^[A-Z0-9_]+$"
    )
    default_timeframe: Timeframe | None = None
    selected_indicators: list[str] | None = Field(default=None, max_length=20)
    theme: Theme | None = None
    timezone: str | None = Field(default=None, min_length=1, max_length=64)
    multi_timeframe_layout: MultiTimeframeLayout | None = None

    @field_validator("default_symbol", mode="before")
    @classmethod
    def normalize_symbol(cls, value: object) -> object:
        return value.strip().upper() if isinstance(value, str) else value

    @field_validator("selected_indicators")
    @classmethod
    def validate_indicators(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        normalized = [indicator.strip().lower() for indicator in value]
        if any(not INDICATOR_PATTERN.fullmatch(indicator) for indicator in normalized):
            raise ValueError("Indicators must use lowercase slug names.")
        if len(set(normalized)) != len(normalized):
            raise ValueError("Indicators must be unique.")
        return normalized

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str | None) -> str | None:
        if value is None:
            return value
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as error:
            raise ValueError("Timezone must be a valid IANA timezone.") from error
        return value
