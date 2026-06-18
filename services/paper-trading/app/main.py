from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    default_trading_mode: str = "paper"
    service_name: str = "paper-trading"


settings = Settings()
app = FastAPI(title="Paper Trading Service", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok", "mode": settings.default_trading_mode}


@app.get("/capabilities")
async def capabilities() -> dict[str, list[str]]:
    return {"capabilities": ["simulated-orders", "positions", "portfolio-pnl", "fill-simulation"]}

