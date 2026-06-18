from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import health, modules, safety

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

app.include_router(health.router)
app.include_router(safety.router, prefix="/safety", tags=["safety"])
app.include_router(modules.router, prefix="/modules", tags=["modules"])


@app.get("/")
async def root() -> dict[str, str]:
    return {"name": "trading-framework-api", "status": "ready"}

