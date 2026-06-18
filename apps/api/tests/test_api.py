from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_safety_defaults_block_live_trading() -> None:
    response = client.get("/safety")

    assert response.status_code == 200
    body = response.json()
    assert body["default_trading_mode"] == "paper"
    assert body["live_trading_enabled"] is False
    assert body["exchange_writes_allowed"] is False

