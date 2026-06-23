from fastapi import APIRouter

from app.api.routes import health, market_websocket, modules, safety, symbols

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(safety.router, prefix="/safety", tags=["safety"])
api_router.include_router(modules.router, prefix="/modules", tags=["modules"])
api_router.include_router(symbols.router, prefix="/symbols", tags=["symbols"])
api_router.include_router(market_websocket.router, tags=["market-websocket"])
