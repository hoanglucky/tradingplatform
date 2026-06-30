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


def layout_payload(symbol: str = "XAUUSD") -> dict[str, object]:
    return {
        "symbol": symbol,
        "windowCount": 4,
        "windows": [
            {
                "id": f"w{index + 1}",
                "timeframe": timeframe,
                "enabled": True,
                "reviewChecked": index == 0,
            }
            for index, timeframe in enumerate(("4h", "1h", "15m", "5m"))
        ],
    }


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
    assert payload["multi_timeframe_layout"] is None


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


def test_patch_settings_persists_multi_timeframe_layout() -> None:
    layout = layout_payload()

    response = client.patch("/settings", json={"multi_timeframe_layout": layout})

    assert response.status_code == 200
    assert response.json()["multi_timeframe_layout"] == layout
    assert client.get("/settings").json()["multi_timeframe_layout"] == layout


def test_patch_settings_rejects_unknown_layout_symbol() -> None:
    response = client.patch(
        "/settings",
        json={"multi_timeframe_layout": layout_payload("NOTREALUSD")},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Active multi-timeframe symbol not found."


@pytest.mark.parametrize(
    ("payload", "error_fragment"),
    [
        ({"default_timeframe": "2m"}, "Input should be"),
        ({"theme": "purple"}, "Input should be"),
        ({"selected_indicators": ["rsi", "RSI"]}, "Indicators must be unique"),
        ({"timezone": "Mars/Olympus"}, "valid IANA timezone"),
        (
            {
                "multi_timeframe_layout": {
                    **layout_payload(),
                    "windowCount": 2,
                }
            },
            "Enabled window count must match windowCount",
        ),
        (
            {
                "multi_timeframe_layout": {
                    **layout_payload(),
                    "windows": [
                        *layout_payload()["windows"][:3],
                        {
                            "id": "w3",
                            "timeframe": "5m",
                            "enabled": True,
                            "reviewChecked": False,
                        },
                    ],
                }
            },
            "window ids must be unique",
        ),
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
