from typing import Literal

from fastapi import APIRouter
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.schemas.health import DependencyStatus, HealthStatus, ReadinessStatus

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthStatus)
async def health() -> HealthStatus:
    return HealthStatus(
        status="ok",
        service="trading-framework-api",
        environment=settings.app_env,
        trading_mode=settings.default_trading_mode,
    )


@router.get("/health/ready", response_model=ReadinessStatus)
async def readiness() -> ReadinessStatus:
    dependencies = [
        await check_postgres(),
        await check_redis(),
    ]
    status: Literal["ready", "degraded"] = (
        "ready" if all(dependency.status == "ok" for dependency in dependencies) else "degraded"
    )

    return ReadinessStatus(status=status, dependencies=dependencies)


async def check_postgres() -> DependencyStatus:
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception as exc:
        return DependencyStatus(name="postgres", status="error", detail=exc.__class__.__name__)
    finally:
        await engine.dispose()

    return DependencyStatus(name="postgres", status="ok")


async def check_redis() -> DependencyStatus:
    client = Redis.from_url(settings.redis_url, socket_connect_timeout=2, socket_timeout=2)
    try:
        await client.ping()
    except Exception as exc:
        return DependencyStatus(name="redis", status="error", detail=exc.__class__.__name__)
    finally:
        await client.aclose()

    return DependencyStatus(name="redis", status="ok")

