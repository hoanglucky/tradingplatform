from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


Timeframe = Literal["1m", "5m", "15m", "1h", "4h", "1d"]


class MarketSubscription(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    type: Literal["subscribe"]
    symbol: str = Field(min_length=2, max_length=24, pattern=r"^[A-Z0-9_]+$")
    timeframe: Timeframe

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_symbol(cls, value: object) -> object:
        return value.upper() if isinstance(value, str) else value


class MarketSubscribed(BaseModel):
    type: Literal["subscribed"] = "subscribed"
    symbol: str
    timeframe: Timeframe
    source: Literal["binance"] = "binance"
    mock: Literal[False] = False


class MarketPong(BaseModel):
    type: Literal["pong"]
    id: int = Field(ge=1)


class MarketHeartbeat(BaseModel):
    type: Literal["heartbeat"] = "heartbeat"
    id: int = Field(ge=1)
    timestamp: datetime


class MarketCandleUpdate(BaseModel):
    type: Literal["candle"] = "candle"
    symbol: str
    timeframe: Timeframe
    timestamp: datetime
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0)
    closed: bool
    source: Literal["binance"] = "binance"
    mock: Literal[False] = False

    @model_validator(mode="after")
    def validate_ohlc_range(self) -> "MarketCandleUpdate":
        if self.low > min(self.open, self.close) or self.high < max(
            self.open, self.close
        ):
            raise ValueError("OHLC values are inconsistent")
        return self


class MarketWebSocketError(BaseModel):
    type: Literal["error"] = "error"
    code: str
    message: str
