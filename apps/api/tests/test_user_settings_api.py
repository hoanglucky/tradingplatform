from __future__ import annotations

import asyncio
import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


async def delete_test_user(email: str) -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(delete(User).where(User.email == email))
        await session.commit()


@pytest.fixture(autouse=True)
def isolated_mvp_user(monkeypatch) -> Generator[str, None, None]:
    email = f"settings-{uuid.uuid4().hex}@trading-framework.test"
    monkeypatch.setattr(settings, "mvp_user_email", email)
    yield email
    asyncio.run(delete_test_user(email))


def test_get_settings_creates_defaults_for_mvp_user() -> None:
    user = client.get("/users/me").json()

    response = client.get("/settings")

    assert response.status_code == 200
    payload = response.json()
    assert payload["user_id"] == user["id"]
    assert payload["default_symbol"] == "BTCUSDT"
    assert payload["default_timeframe"] == "15m"
    assert payload["selected_indicators"] == []
    assert payload["theme"] == "system"
    assert payload["timezone"] == "UTC"


def test_patch_settings_persists_partial_preferences() -> None:
    response = client.patch(
        "/settings",
        json={
            "default_symbol": "xauusd",
            "default_timeframe": "5m",
            "selected_indicators": ["SMA", "rsi_14"],
            "theme": "dark",
            "timezone": "Asia/Bangkok",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["default_symbol"] == "XAUUSD"
    assert payload["default_timeframe"] == "5m"
    assert payload["selected_indicators"] == ["sma", "rsi_14"]
    assert payload["theme"] == "dark"
    assert payload["timezone"] == "Asia/Bangkok"
    assert client.get("/settings").json()["default_symbol"] == "XAUUSD"


def test_patch_settings_rejects_unknown_symbol() -> None:
    response = client.patch("/settings", json={"default_symbol": "NOTREALUSD"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Active default symbol not found."


@pytest.mark.parametrize(
    ("payload", "error_fragment"),
    [
        ({"default_timeframe": "2m"}, "Input should be"),
        ({"theme": "purple"}, "Input should be"),
        ({"selected_indicators": ["rsi", "RSI"]}, "Indicators must be unique"),
        ({"timezone": "Mars/Olympus"}, "valid IANA timezone"),
    ],
)
def test_patch_settings_validates_preferences(
    payload: dict[str, object], error_fragment: str
) -> None:
    response = client.patch("/settings", json=payload)

    assert response.status_code == 422
    assert error_fragment in response.text


def test_settings_endpoints_are_in_openapi_schema() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/settings" in response.json()["paths"]
