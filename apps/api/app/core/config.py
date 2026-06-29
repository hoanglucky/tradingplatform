from functools import cached_property
from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_env: str = "development"
    log_level: str = "info"
    database_url: str = (
        "postgresql+asyncpg://trader:trader@localhost:5432/trading_framework"
    )
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:2000"
    binance_ws_base_url: str = "wss://data-stream.binance.vision/ws"
    oanda_api_token: str = ""
    oanda_environment: str = "practice"
    oanda_realtime_poll_seconds: float = Field(default=2.0, ge=0.5, le=60)
    market_stream_reconnect_seconds: float = Field(default=1.0, gt=0, le=60)
    market_stream_max_reconnect_seconds: float = Field(default=30.0, gt=0, le=300)
    market_ws_heartbeat_seconds: float = Field(default=10.0, gt=0, le=60)
    market_ws_stale_seconds: float = Field(default=30.0, gt=0, le=300)
    mvp_user_mode: bool = True
    mvp_user_email: str = Field(
        default="local@trading-framework.test", min_length=3, max_length=320
    )
    mvp_user_display_name: str = Field(
        default="Local Trader", min_length=1, max_length=120
    )
    mvp_watchlist_name: str = Field(default="Main", min_length=1, max_length=120)
    enable_live_trading: bool = False
    enable_exchange_writes: bool = False
    default_trading_mode: str = "paper"
    exchange_adapter_mode: str = "read_only"

    @model_validator(mode="after")
    def validate_websocket_timing(self) -> Self:
        if self.market_ws_stale_seconds <= self.market_ws_heartbeat_seconds:
            raise ValueError(
                "MARKET_WS_STALE_SECONDS must be greater than MARKET_WS_HEARTBEAT_SECONDS"
            )
        return self

    @cached_property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def live_trading_enabled(self) -> bool:
        return self.enable_live_trading and self.enable_exchange_writes

    @property
    def exchange_writes_allowed(self) -> bool:
        return (
            self.exchange_adapter_mode == "write_enabled" and self.live_trading_enabled
        )


settings = Settings()
