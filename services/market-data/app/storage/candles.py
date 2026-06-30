from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, MetaData, Numeric, String, Table, func, select
from sqlalchemy.dialects.postgresql import UUID, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import Candle

metadata = MetaData()

symbols_table = Table(
    "symbols",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("exchange", String(40), nullable=False),
    Column("symbol", String(40), nullable=False),
    Column("base_asset", String(24), nullable=False),
    Column("quote_asset", String(24), nullable=False),
    Column("is_active", Boolean, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

candles_table = Table(
    "candles",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("symbol_id", UUID(as_uuid=True), nullable=False),
    Column("timeframe", String(16), nullable=False),
    Column("timestamp", DateTime(timezone=True), nullable=False),
    Column("open", Numeric(20, 8), nullable=False),
    Column("high", Numeric(20, 8), nullable=False),
    Column("low", Numeric(20, 8), nullable=False),
    Column("close", Numeric(20, 8), nullable=False),
    Column("volume", Numeric(28, 8), nullable=False),
    Column("partial", Boolean, nullable=False),
    Column("complete", Boolean, nullable=False),
    Column("source_count", Integer, nullable=True),
    Column("expected_source_count", Integer, nullable=True),
    Column("missing_source_count", Integer, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


class SymbolNotFoundError(LookupError):
    pass


class CandleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_symbol_id(self, symbol: str, exchange: str | None = None) -> uuid.UUID | None:
        normalized = symbol.upper().replace("/", "").replace("-", "").replace("_", "")
        query = select(symbols_table.c.id).where(
            func.upper(symbols_table.c.symbol) == normalized,
            symbols_table.c.is_active.is_(True),
        )
        if exchange:
            query = query.order_by((symbols_table.c.exchange != exchange).asc())
        result = await self.session.execute(query.limit(1))
        return result.scalar_one_or_none()

    async def list_range(
        self,
        symbol_id: uuid.UUID,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        query = (
            select(candles_table)
            .where(
                candles_table.c.symbol_id == symbol_id,
                candles_table.c.timeframe == timeframe,
                candles_table.c.timestamp >= start,
                candles_table.c.timestamp < end,
            )
            .order_by(candles_table.c.timestamp.asc())
        )
        rows = (await self.session.execute(query)).mappings().all()
        return [
            Candle(
                symbol=symbol.upper(),
                timeframe=row["timeframe"],
                timestamp=row["timestamp"],
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["volume"],
                partial=row["partial"],
                complete=row["complete"],
                source_count=row["source_count"],
                expected_source_count=row["expected_source_count"],
                missing_source_count=row["missing_source_count"],
            )
            for row in rows
        ]

    async def upsert_many(self, symbol_id: uuid.UUID, candles: list[Candle]) -> None:
        if not candles:
            return

        values = [
            {
                "id": uuid.uuid4(),
                "symbol_id": symbol_id,
                "timeframe": candle.timeframe,
                "timestamp": candle.timestamp,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume,
                "partial": candle.partial,
                "complete": candle.complete,
                "source_count": candle.source_count,
                "expected_source_count": candle.expected_source_count,
                "missing_source_count": candle.missing_source_count,
                "created_at": func.now(),
                "updated_at": func.now(),
            }
            for candle in candles
        ]
        statement = insert(candles_table).values(values)
        statement = statement.on_conflict_do_update(
            index_elements=["symbol_id", "timeframe", "timestamp"],
            set_={
                "open": statement.excluded.open,
                "high": statement.excluded.high,
                "low": statement.excluded.low,
                "close": statement.excluded.close,
                "volume": statement.excluded.volume,
                "partial": statement.excluded.partial,
                "complete": statement.excluded.complete,
                "source_count": statement.excluded.source_count,
                "expected_source_count": statement.excluded.expected_source_count,
                "missing_source_count": statement.excluded.missing_source_count,
                "updated_at": func.now(),
            },
        )
        await self.session.execute(statement)

    async def commit(self) -> None:
        await self.session.commit()
