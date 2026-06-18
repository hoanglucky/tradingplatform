from fastapi.testclient import TestClient

from app.api.routes import health as health_routes
from app.main import app
from app.schemas.health import DependencyStatus


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "trading-framework-api"
    assert body["trading_mode"] == "paper"


def test_readiness_reports_ready_when_dependencies_are_ok(monkeypatch) -> None:
    async def ok_postgres() -> DependencyStatus:
        return DependencyStatus(name="postgres", status="ok")

    async def ok_redis() -> DependencyStatus:
        return DependencyStatus(name="redis", status="ok")

    monkeypatch.setattr(health_routes, "check_postgres", ok_postgres)
    monkeypatch.setattr(health_routes, "check_redis", ok_redis)

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_readiness_reports_degraded_when_dependency_fails(monkeypatch) -> None:
    async def failed_postgres() -> DependencyStatus:
        return DependencyStatus(name="postgres", status="error", detail="ConnectionError")

    async def ok_redis() -> DependencyStatus:
        return DependencyStatus(name="redis", status="ok")

    monkeypatch.setattr(health_routes, "check_postgres", failed_postgres)
    monkeypatch.setattr(health_routes, "check_redis", ok_redis)

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "degraded"


def test_safety_defaults_block_live_trading() -> None:
    response = client.get("/safety")

    assert response.status_code == 200
    body = response.json()
    assert body["default_trading_mode"] == "paper"
    assert body["live_trading_enabled"] is False
    assert body["exchange_writes_allowed"] is False
