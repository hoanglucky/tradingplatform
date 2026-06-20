from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.market import router as market_router
from app.config import settings
app = FastAPI(title="Market Data Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(market_router, prefix="/market", tags=["market"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok"}


@app.get("/capabilities")
async def capabilities() -> dict[str, list[str]]:
    return {
        "capabilities": [
            "market-data-provider-interface",
            "oanda-read-only-candles",
            "postgres-candle-cache",
            "quote-normalization",
            "candle-ingestion",
            "market-data-events",
        ]
    }
