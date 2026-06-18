from pydantic import BaseModel


class SafetyStatus(BaseModel):
    default_trading_mode: str
    live_trading_enabled: bool
    exchange_writes_allowed: bool
    exchange_adapter_mode: str

