from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import logger, setup_logging

setup_logging()

app = FastAPI(
    title="Trading Framework API",
    version="0.1.0",
    description="Backend API for a paper-first trading MVP.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    logger.debug("Root endpoint requested")
    return {"name": "trading-framework-api", "status": "ready"}
