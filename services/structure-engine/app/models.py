from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StructureModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Candle(StructureModel):
    symbol: str = Field(min_length=1)
    timeframe: str = Field(min_length=1)
    timestamp: datetime
    open: Decimal = Field(gt=0)
    high: Decimal = Field(gt=0)
    low: Decimal = Field(gt=0)
    close: Decimal = Field(gt=0)
    volume: Decimal | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_candle(self) -> Candle:
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        if self.high < max(self.open, self.close) or self.low > min(
            self.open, self.close
        ):
            raise ValueError("OHLC values are inconsistent")
        if self.low > self.high:
            raise ValueError("low cannot exceed high")
        return self


class SwingDirection(StrEnum):
    HIGH = "HIGH"
    LOW = "LOW"


class SwingPoint(StructureModel):
    id: str = Field(min_length=1)
    symbol: str = Field(min_length=1)
    timeframe: str = Field(min_length=1)
    candle_index: int = Field(ge=0)
    timestamp: datetime
    price: Decimal = Field(gt=0)
    direction: SwingDirection
    confirmed: bool = True

    @model_validator(mode="after")
    def validate_timestamp(self) -> SwingPoint:
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return self


class StructureConfig(StructureModel):
    left_bars: int = Field(default=2, ge=1)
    right_bars: int = Field(default=2, ge=1)
    min_distance: Decimal = Field(default=Decimal("0"), ge=0)


class MarketStructureState(StructureModel):
    symbol: str = Field(min_length=1)
    timeframe: str = Field(min_length=1)
    candle_count: int = Field(ge=0)
    swings: tuple[SwingPoint, ...] = ()
    analyzed_at: datetime

    @model_validator(mode="after")
    def validate_state(self) -> MarketStructureState:
        if self.analyzed_at.tzinfo is None or self.analyzed_at.utcoffset() is None:
            raise ValueError("analyzed_at must be timezone-aware")
        for swing in self.swings:
            if swing.symbol != self.symbol or swing.timeframe != self.timeframe:
                raise ValueError("swing identity must match the structure state")
            if swing.candle_index >= self.candle_count:
                raise ValueError("swing candle_index must reference an analyzed candle")
        return self
