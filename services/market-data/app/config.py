from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql+asyncpg://trader:trader@localhost:5432/trading_framework"
    service_name: str = "market-data"
    cors_origins: str = "http://localhost:2000"
    oanda_api_token: str = ""
    oanda_account_id: str = ""
    oanda_environment: str = "practice"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
