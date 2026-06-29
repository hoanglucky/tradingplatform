from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.main import app
from app.services.mvp_user import ensure_mvp_user

client = TestClient(app)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.mark.anyio
async def test_ensure_mvp_user_is_idempotent(
    db_session: AsyncSession, monkeypatch
) -> None:
    email = f"local-{uuid.uuid4().hex}@trading-framework.test"
    monkeypatch.setattr(settings, "mvp_user_email", email)
    first_user, first_created = await ensure_mvp_user(db_session)
    second_user, second_created = await ensure_mvp_user(db_session)

    assert first_user.id == second_user.id
    assert first_user.email == email
    assert first_created is True
    assert second_created is False


def test_users_me_creates_and_identifies_mvp_user() -> None:
    first_response = client.get("/users/me")
    second_response = client.get("/users/me")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    first_user = first_response.json()
    second_user = second_response.json()
    assert first_user["id"] == second_user["id"]
    assert first_user["email"] == settings.mvp_user_email
    assert first_user["display_name"] == settings.mvp_user_display_name
    assert first_user["mode"] == "mvp_local"


def test_users_me_is_unavailable_when_mvp_mode_is_disabled(monkeypatch) -> None:
    monkeypatch.setattr(settings, "mvp_user_mode", False)

    response = client.get("/users/me")

    assert response.status_code == 503
    assert (
        response.json()["detail"]
        == "MVP user mode is disabled and authentication is not configured."
    )


def test_users_me_is_in_openapi_schema() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/users/me" in response.json()["paths"]
