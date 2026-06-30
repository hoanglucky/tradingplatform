from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.structure_engine import TLPConfig, analyze_tlp_structure


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    service_name: str = "structure-engine"


settings = Settings()
app = FastAPI(title="Structure Engine", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:2000", "http://127.0.0.1:2000"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class AnalyzeCandle(BaseModel):
    model_config = ConfigDict(extra="ignore")

    timestamp: str = Field(min_length=1)
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(default=0, ge=0)


class AnalyzeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    show_tlp: bool = True
    show_inside_bars: bool = False
    show_outside_bars: bool = True
    detect_inside_bar_zones: bool = True
    include_swing_markers: bool = True


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(min_length=1)
    timeframe: str = Field(min_length=1)
    candles: list[AnalyzeCandle] = Field(min_length=1, max_length=5000)
    config: AnalyzeConfig = Field(default_factory=AnalyzeConfig)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"service": settings.service_name, "status": "ok"}


@app.get("/capabilities")
async def capabilities() -> dict[str, list[str]]:
    return {
        "capabilities": [
            "structure-types",
            "price-structure-analysis",
            "tlp-swing-overlay",
        ]
    }


@app.post("/structure/analyze")
async def analyze_structure(request: AnalyzeRequest) -> dict[str, Any]:
    result = analyze_tlp_structure(
        [candle.model_dump() for candle in request.candles],
        TLPConfig(**request.config.model_dump()),
    )
    result["metadata"].update(
        {"symbol": request.symbol.upper(), "timeframe": request.timeframe}
    )
    return result
