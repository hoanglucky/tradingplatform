from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def unique_symbol_payload() -> dict[str, object]:
    suffix = uuid.uuid4().hex[:8].upper()
    return {
        "exchange": "binance",
        "symbol": f"API{suffix}USDT",
        "base_asset": f"API{suffix}",
        "quote_asset": "USDT",
        "is_active": True,
    }


def test_symbol_crud_api() -> None:
    payload = unique_symbol_payload()

    create_response = client.post("/symbols", json=payload)
    assert create_response.status_code == 201
    created = create_response.json()
    symbol_id = created["id"]
    assert created["symbol"] == payload["symbol"]
    assert created["is_active"] is True

    list_response = client.get("/symbols")
    assert list_response.status_code == 200
    assert any(symbol["id"] == symbol_id for symbol in list_response.json())

    get_response = client.get(f"/symbols/{symbol_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == symbol_id

    active_response = client.get("/symbols", params={"active_only": True})
    assert active_response.status_code == 200
    assert any(symbol["id"] == symbol_id for symbol in active_response.json())

    update_response = client.patch(f"/symbols/{symbol_id}", json={"is_active": False})
    assert update_response.status_code == 200
    assert update_response.json()["is_active"] is False

    inactive_response = client.get("/symbols", params={"active_only": True})
    assert inactive_response.status_code == 200
    assert all(symbol["id"] != symbol_id for symbol in inactive_response.json())

    delete_response = client.delete(f"/symbols/{symbol_id}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/symbols/{symbol_id}")
    assert missing_response.status_code == 404


def test_create_duplicate_symbol_returns_conflict() -> None:
    payload = unique_symbol_payload()

    first_response = client.post("/symbols", json=payload)
    assert first_response.status_code == 201
    symbol_id = first_response.json()["id"]

    duplicate_response = client.post("/symbols", json=payload)
    assert duplicate_response.status_code == 409

    cleanup_response = client.delete(f"/symbols/{symbol_id}")
    assert cleanup_response.status_code == 204


def test_update_missing_symbol_returns_not_found() -> None:
    response = client.patch(f"/symbols/{uuid.uuid4()}", json={"is_active": False})

    assert response.status_code == 404


def test_symbol_endpoints_are_in_openapi_schema() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/symbols" in paths
    assert "/symbols/{symbol_id}" in paths
