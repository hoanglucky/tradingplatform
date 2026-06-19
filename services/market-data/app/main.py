from fastapi import FastAPI

from app.config import settings
app = FastAPI(title="Market Data Service", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok"}


@app.get("/capabilities")
async def capabilities() -> dict[str, list[str]]:
    return {
        "capabilities": [
            "market-data-provider-interface",
            "oanda-read-only-candles",
            "quote-normalization",
            "candle-ingestion",
            "market-data-events",
        ]
    }
