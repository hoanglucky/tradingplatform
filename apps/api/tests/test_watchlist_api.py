from __future__ import annotations

import asyncio
import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.user import User
from app.models.watchlist import Watchlist

client = TestClient(app)


async def clear_default_watchlist() -> None:
    async with AsyncSessionLocal() as session:
        user_id = await session.scalar(
            select(User.id).where(User.email == settings.mvp_user_email)
        )
        if user_id is not None:
            await session.execute(delete(Watchlist).where(Watchlist.user_id == user_id))
            await session.commit()


async def delete_test_user(email: str) -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(delete(User).where(User.email == email))
        await session.commit()


@pytest.fixture(autouse=True)
def isolated_mvp_user(monkeypatch) -> Generator[str, None, None]:
    email = f"watchlist-{uuid.uuid4().hex}@trading-framework.test"
    monkeypatch.setattr(settings, "mvp_user_email", email)
    yield email
    asyncio.run(delete_test_user(email))


@pytest.fixture
def watchlist_symbol(isolated_mvp_user: str) -> Generator[str, None, None]:
    asyncio.run(clear_default_watchlist())
    suffix = uuid.uuid4().hex[:8].upper()
    symbol = f"WL{suffix}USD"
    response = client.post(
        "/symbols",
        json={
            "exchange": "test",
            "symbol": symbol,
            "base_asset": f"WL{suffix}",
            "quote_asset": "USD",
            "is_active": True,
        },
    )
    assert response.status_code == 201
    symbol_id = response.json()["id"]

    yield symbol

    asyncio.run(clear_default_watchlist())
    assert client.delete(f"/symbols/{symbol_id}").status_code == 204


def test_watchlist_crud_uses_mvp_user(watchlist_symbol: str) -> None:
    user = client.get("/users/me").json()

    empty_response = client.get("/watchlist")
    assert empty_response.status_code == 200
    assert empty_response.json()["user_id"] == user["id"]
    assert empty_response.json()["items"] == []

    create_response = client.post(
        "/watchlist/items", json={"symbol": watchlist_symbol.lower()}
    )
    assert create_response.status_code == 201
    assert create_response.json()["symbol"] == watchlist_symbol

    list_response = client.get("/watchlist")
    assert [item["symbol"] for item in list_response.json()["items"]] == [
        watchlist_symbol
    ]

    delete_response = client.delete(f"/watchlist/items/{watchlist_symbol.lower()}")
    assert delete_response.status_code == 204
    assert client.get("/watchlist").json()["items"] == []


def test_watchlist_rejects_duplicate_symbol(watchlist_symbol: str) -> None:
    first_response = client.post("/watchlist/items", json={"symbol": watchlist_symbol})
    duplicate_response = client.post(
        "/watchlist/items", json={"symbol": watchlist_symbol}
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == "Symbol already exists in watchlist."


def test_watchlist_rejects_unknown_symbol() -> None:
    asyncio.run(clear_default_watchlist())

    response = client.post("/watchlist/items", json={"symbol": "NOTREALUSD"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Active symbol not found."


def test_watchlist_rejects_inactive_symbol(watchlist_symbol: str) -> None:
    symbols = client.get("/symbols").json()
    symbol_id = next(
        item["id"] for item in symbols if item["symbol"] == watchlist_symbol
    )
    assert (
        client.patch(f"/symbols/{symbol_id}", json={"is_active": False}).status_code
        == 200
    )

    response = client.post("/watchlist/items", json={"symbol": watchlist_symbol})

    assert response.status_code == 404
    assert response.json()["detail"] == "Active symbol not found."


def test_watchlist_delete_missing_item_returns_not_found(watchlist_symbol: str) -> None:
    response = client.delete(f"/watchlist/items/{watchlist_symbol}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Watchlist item not found."


def test_watchlist_endpoints_are_in_openapi_schema() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/watchlist" in paths
    assert "/watchlist/items" in paths
    assert "/watchlist/items/{symbol}" in paths
