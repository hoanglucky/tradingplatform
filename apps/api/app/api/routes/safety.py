from fastapi import APIRouter

from app.core.config import settings
from app.schemas.safety import SafetyStatus

router = APIRouter()


@router.get("", response_model=SafetyStatus)
async def safety_status() -> SafetyStatus:
    return SafetyStatus(
        default_trading_mode=settings.default_trading_mode,
        live_trading_enabled=settings.live_trading_enabled,
        exchange_writes_allowed=settings.exchange_writes_allowed,
        exchange_adapter_mode=settings.exchange_adapter_mode,
    )

