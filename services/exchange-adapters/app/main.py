from fastapi import FastAPI, HTTPException, status
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    exchange_adapter_mode: str = "read_only"
    enable_live_trading: bool = False
    enable_exchange_writes: bool = False
    service_name: str = "exchange-adapters"

    @property
    def writes_allowed(self) -> bool:
        return (
            self.exchange_adapter_mode == "write_enabled"
            and self.enable_live_trading
            and self.enable_exchange_writes
        )


settings = Settings()
app = FastAPI(title="Exchange Adapters", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str | bool]:
    return {
        "service": settings.service_name,
        "status": "ok",
        "mode": settings.exchange_adapter_mode,
        "writes_allowed": settings.writes_allowed,
    }


@app.get("/capabilities")
async def capabilities() -> dict[str, list[str]]:
    return {"capabilities": ["read-only-market-data", "read-only-account-data"]}


@app.post("/orders")
async def create_order() -> dict[str, str]:
    if not settings.writes_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Exchange writes are disabled. This scaffold does not implement live trading.",
        )
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Live order placement is intentionally not implemented.",
    )

