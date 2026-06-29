from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.symbol import Symbol
from app.repositories.base import BaseRepository


class SymbolRepository(BaseRepository[Symbol]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Symbol)

    async def get_by_symbol(self, exchange: str, symbol: str) -> Symbol | None:
        result = await self.session.scalars(
            select(Symbol).where(Symbol.exchange == exchange, Symbol.symbol == symbol)
        )
        return result.first()

    async def get_active_by_symbol(self, symbol: str) -> Symbol | None:
        result = await self.session.scalars(
            select(Symbol)
            .where(Symbol.symbol == symbol, Symbol.is_active.is_(True))
            .order_by(Symbol.exchange)
        )
        return result.first()

    async def list_active(self, *, limit: int = 100, offset: int = 0) -> list[Symbol]:
        result = await self.session.scalars(
            select(Symbol).where(Symbol.is_active.is_(True)).offset(offset).limit(limit)
        )
        return list(result.all())
