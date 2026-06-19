from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.repositories.symbols import SymbolRepository


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.mark.anyio
async def test_symbol_repository_crud(db_session: AsyncSession) -> None:
    repo = SymbolRepository(db_session)
    suffix = uuid.uuid4().hex[:8].upper()

    symbol = await repo.create(
        exchange="binance",
        symbol=f"TST{suffix}USDT",
        base_asset=f"TST{suffix}",
        quote_asset="USDT",
    )

    assert symbol.id is not None
    assert symbol.is_active is True

    fetched = await repo.get_by_id(symbol.id)
    assert fetched is not None
    assert fetched.symbol == symbol.symbol

    by_symbol = await repo.get_by_symbol("binance", symbol.symbol)
    assert by_symbol is not None
    assert by_symbol.id == symbol.id

    listed = await repo.list()
    assert any(item.id == symbol.id for item in listed)

    active = await repo.list_active()
    assert any(item.id == symbol.id for item in active)

    updated = await repo.update(symbol.id, is_active=False)
    assert updated is not None
    assert updated.is_active is False

    deleted = await repo.delete(symbol.id)
    assert deleted is True
    assert await repo.get_by_id(symbol.id) is None
