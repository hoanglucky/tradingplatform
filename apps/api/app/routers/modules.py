from fastapi import APIRouter

from app.schemas.module import ModuleStatus

router = APIRouter()

MODULES = [
    ModuleStatus(name="market-data", role="Normalize quotes, candles, and order book snapshots.", status="scaffolded"),
    ModuleStatus(name="indicator-engine", role="Compute technical indicators from normalized market data.", status="scaffolded"),
    ModuleStatus(name="strategy-engine", role="Evaluate strategies and emit paper-trading signals.", status="scaffolded"),
    ModuleStatus(name="backtest-engine", role="Replay historical data and calculate performance metrics.", status="scaffolded"),
    ModuleStatus(name="paper-trading", role="Simulate orders, fills, positions, and portfolio PnL.", status="scaffolded"),
    ModuleStatus(name="alert-engine", role="Route notifications for signals, risk events, and system health.", status="scaffolded"),
    ModuleStatus(name="exchange-adapters", role="Read-only exchange connectivity until explicitly enabled.", status="read_only"),
]


@router.get("", response_model=list[ModuleStatus])
async def list_modules() -> list[ModuleStatus]:
    return MODULES

