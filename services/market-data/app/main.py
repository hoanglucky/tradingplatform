from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    redis_url: str = "redis://localhost:6379/0"
    service_name: str = "market-data"


settings = Settings()
app = FastAPI(title="Market Data Service", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok"}


@app.get("/capabilities")
async def capabilities() -> dict[str, list[str]]:
    return {"capabilities": ["quote-normalization", "candle-ingestion", "market-data-events"]}

