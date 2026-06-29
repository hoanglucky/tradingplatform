from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator

Timeframe = Literal["1m", "5m", "15m", "1h", "4h", "1d"]
Theme = Literal["light", "dark", "system"]
INDICATOR_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,31}$")


class UserSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    default_symbol: str
    default_timeframe: Timeframe
    selected_indicators: list[str]
    theme: Theme
    timezone: str
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
