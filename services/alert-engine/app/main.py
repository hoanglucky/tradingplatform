from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    alert_webhook_url: str = ""
    service_name: str = "alert-engine"


settings = Settings()
app = FastAPI(title="Alert Engine", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok"}


@app.get("/capabilities")
async def capabilities() -> dict[str, list[str]]:
    return {"capabilities": ["webhook-alerts", "email-alerts", "signal-notifications", "risk-alerts"]}

