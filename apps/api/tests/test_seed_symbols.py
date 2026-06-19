from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.repositories.symbols import SymbolRepository
from app.seed.symbols import DEFAULT_SYMBOLS, seed_symbols


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.mark.anyio
async def test_seed_symbols_is_idempotent(db_session: AsyncSession) -> None:
    repo = SymbolRepository(db_session)

    first_result = await seed_symbols(db_session)
    second_result = await seed_symbols(db_session)

    assert first_result.created + first_result.updated + first_result.skipped == len(DEFAULT_SYMBOLS)
    assert second_result.created == 0
    assert second_result.updated == 0
    assert second_result.skipped == len(DEFAULT_SYMBOLS)

    for symbol_data in DEFAULT_SYMBOLS:
        symbol = await repo.get_by_symbol(symbol_data["exchange"], symbol_data["symbol"])
        assert symbol is not None
        assert symbol.is_active is True
