from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator


class MarketSymbol(BaseModel):
    exchange: str = Field(min_length=1, max_length=40)
    symbol: str = Field(min_length=1, max_length=40)
    base_asset: str = Field(min_length=1, max_length=24)
    quote_asset: str = Field(min_length=1, max_length=24)
    is_active: bool = True


class Candle(BaseModel):
    symbol: str = Field(min_length=1, max_length=40)
    timeframe: str = Field(min_length=1, max_length=16)
    timestamp: datetime
    open: Decimal = Field(gt=0)
    high: Decimal = Field(gt=0)
    low: Decimal = Field(gt=0)
    close: Decimal = Field(gt=0)
    volume: Decimal = Field(ge=0)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_have_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return value


class AggregatedCandle(Candle):
    closed: bool
    partial: bool

    @model_validator(mode="after")
    def closed_and_partial_are_complementary(self) -> "AggregatedCandle":
        if self.closed == self.partial:
            raise ValueError("An aggregated candle must be either closed or partial.")
        return self


class LatestPrice(BaseModel):
    symbol: str = Field(min_length=1, max_length=40)
    timestamp: datetime
    price: Decimal = Field(gt=0)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_have_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return value
