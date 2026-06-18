from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    log_level: str = "info"
    database_url: str = "postgresql+asyncpg://trader:trader@localhost:5432/trading_framework"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:3000"
    enable_live_trading: bool = False
    enable_exchange_writes: bool = False
    default_trading_mode: str = "paper"
    exchange_adapter_mode: str = "read_only"

    @cached_property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def live_trading_enabled(self) -> bool:
        return self.enable_live_trading and self.enable_exchange_writes

    @property
    def exchange_writes_allowed(self) -> bool:
        return self.exchange_adapter_mode == "write_enabled" and self.live_trading_enabled


settings = Settings()
