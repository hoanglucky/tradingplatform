from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy import delete, func
from sqlalchemy.dialects.postgresql import insert

from app.db import AsyncSessionLocal
from app.schemas import Candle
from app.storage.candles import CandleRepository, candles_table, symbols_table


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_postgres_upsert_deduplicates_candles() -> None:
    symbol_id = uuid.uuid4()
    symbol_name = f"TST{uuid.uuid4().hex[:8].upper()}USDT"
    timestamp = datetime(2024, 6, 19, 8, 0, tzinfo=UTC)

    async with AsyncSessionLocal() as session:
        await session.execute(
            insert(symbols_table).values(
                id=symbol_id,
                exchange="test",
                symbol=symbol_name,
                base_asset=symbol_name[:-4],
                quote_asset="USDT",
                is_active=True,
                created_at=func.now(),
                updated_at=func.now(),
            )
        )
        await session.commit()

        repository = CandleRepository(session)
        first = Candle(
            symbol=symbol_name,
            timeframe="1m",
            timestamp=timestamp,
            open=Decimal("100.00"),
            high=Decimal("102.00"),
            low=Decimal("99.00"),
            close=Decimal("101.00"),
            volume=Decimal("10.00"),
        )
        updated = first.model_copy(update={"close": Decimal("101.50")})

        try:
            await repository.upsert_many(symbol_id, [first])
            await repository.commit()
            await repository.upsert_many(symbol_id, [updated])
            await repository.commit()

            candles = await repository.list_range(
                symbol_id,
                symbol_name,
                "1m",
                timestamp,
                datetime(2024, 6, 19, 8, 1, tzinfo=UTC),
            )

            assert len(candles) == 1
            assert candles[0].close == Decimal("101.50000000")
        finally:
            await session.execute(delete(candles_table).where(candles_table.c.symbol_id == symbol_id))
            await session.execute(delete(symbols_table).where(symbols_table.c.id == symbol_id))
            await session.commit()
