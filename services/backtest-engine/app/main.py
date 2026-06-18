from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+asyncpg://trader:trader@localhost:5432/trading_framework"
    service_name: str = "backtest-engine"


settings = Settings()
app = FastAPI(title="Backtest Engine", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok"}


@app.get("/capabilities")
async def capabilities() -> dict[str, list[str]]:
    return {"capabilities": ["historical-replay", "performance-metrics", "result-persistence"]}

