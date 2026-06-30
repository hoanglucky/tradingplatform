from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.adapters.binance import (
    BinanceAdapterError,
    BinancePublicMarketDataProvider,
    BinanceValidationError,
)
from app.adapters.oanda import (
    OANDA_SYMBOL_MAP,
    OandaAdapterError,
    OandaConfigurationError,
    OandaMarketDataProvider,
    OandaValidationError,
)
from app.db import get_db
from app.providers import MarketDataProvider
from app.schemas import Candle
from app.services.candle_storage import CandleStorageService
from app.storage.candles import CandleRepository, SymbolNotFoundError
from app.timeframes import TimeframeValidationError, normalize_timeframe
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_market_data_provider(symbol: str = Query(min_length=1, max_length=40)) -> MarketDataProvider:
    normalized = symbol.upper().replace("/", "").replace("-", "").replace("_", "")
    if normalized in OANDA_SYMBOL_MAP:
        return OandaMarketDataProvider()
    return BinancePublicMarketDataProvider()


def get_candle_storage_service(
    provider: MarketDataProvider = Depends(get_market_data_provider),
    db: AsyncSession = Depends(get_db),
) -> CandleStorageService:
    return CandleStorageService(CandleRepository(db), provider)


@router.get("/candles", response_model=list[Candle])
async def get_market_candles(
    symbol: str = Query(min_length=1, max_length=40),
    timeframe: str = Query(min_length=1, max_length=16),
    start: datetime = Query(),
    end: datetime = Query(),
    service: CandleStorageService = Depends(get_candle_storage_service),
) -> list[Candle]:
    try:
        timeframe = normalize_timeframe(timeframe)
        return await service.get_candles(symbol, timeframe, start, end)
    except SymbolNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (BinanceValidationError, OandaValidationError, TimeframeValidationError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except OandaConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except (BinanceAdapterError, OandaAdapterError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Market data provider request failed.",
        ) from exc
