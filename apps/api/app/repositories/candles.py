from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candle import Candle
from app.repositories.base import BaseRepository


class CandleRepository(BaseRepository[Candle]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Candle)

    async def list_by_symbol(
        self,
        symbol_id: uuid.UUID,
        *,
        timeframe: str | None = None,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        limit: int = 500,
        offset: int = 0,
    ) -> list[Candle]:
        query = select(Candle).where(Candle.symbol_id == symbol_id)
        if timeframe is not None:
            query = query.where(Candle.timeframe == timeframe)
        if start_at is not None:
            query = query.where(Candle.timestamp >= start_at)
        if end_at is not None:
            query = query.where(Candle.timestamp <= end_at)

        result = await self.session.scalars(query.order_by(Candle.timestamp.asc()).offset(offset).limit(limit))
        return list(result.all())
