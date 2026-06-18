from typing import Literal

from pydantic import BaseModel


class HealthStatus(BaseModel):
    status: Literal["ok"]
    service: str
    environment: str
    trading_mode: str


class DependencyStatus(BaseModel):
    name: str
    status: Literal["ok", "error"]
    detail: str | None = None


class ReadinessStatus(BaseModel):
    status: Literal["ready", "degraded"]
    dependencies: list[DependencyStatus]

