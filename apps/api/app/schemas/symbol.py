from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SymbolBase(BaseModel):
    exchange: str = Field(min_length=1, max_length=40)
    symbol: str = Field(min_length=1, max_length=40)
    base_asset: str = Field(min_length=1, max_length=24)
    quote_asset: str = Field(min_length=1, max_length=24)
    is_active: bool = True


class SymbolCreate(SymbolBase):
    pass


class SymbolUpdate(BaseModel):
    exchange: str | None = Field(default=None, min_length=1, max_length=40)
    symbol: str | None = Field(default=None, min_length=1, max_length=40)
    base_asset: str | None = Field(default=None, min_length=1, max_length=24)
    quote_asset: str | None = Field(default=None, min_length=1, max_length=24)
    is_active: bool | None = None


class SymbolRead(SymbolBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
