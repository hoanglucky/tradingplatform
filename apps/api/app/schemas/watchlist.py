from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WatchlistItemCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    symbol: str = Field(min_length=2, max_length=40, pattern=r"^[A-Z0-9_]+$")

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_symbol(cls, value: object) -> object:
        return value.upper() if isinstance(value, str) else value


class WatchlistItemRead(BaseModel):
    id: uuid.UUID
    symbol_id: uuid.UUID
    exchange: str
    symbol: str
    base_asset: str
    quote_asset: str
    created_at: datetime


class WatchlistRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    items: list[WatchlistItemRead]
