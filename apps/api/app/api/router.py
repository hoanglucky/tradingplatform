from fastapi import APIRouter

from app.api.routes import (
    health,
    market_websocket,
    modules,
    safety,
    symbols,
    user_settings,
    users,
    watchlist,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(safety.router, prefix="/safety", tags=["safety"])
api_router.include_router(modules.router, prefix="/modules", tags=["modules"])
api_router.include_router(symbols.router, prefix="/symbols", tags=["symbols"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(user_settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])
api_router.include_router(market_websocket.router, tags=["market-websocket"])
