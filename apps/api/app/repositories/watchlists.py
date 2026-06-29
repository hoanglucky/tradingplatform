from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.symbol import Symbol
from app.models.watchlist import Watchlist, WatchlistItem
from app.repositories.base import BaseRepository


class WatchlistRepository(BaseRepository[Watchlist]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Watchlist)

    async def list_for_user(
        self, user_id: uuid.UUID, *, limit: int = 100, offset: int = 0
    ) -> list[Watchlist]:
        result = await self.session.scalars(
            select(Watchlist)
            .where(Watchlist.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )
        return list(result.all())

    async def get_by_user_and_name(
        self, user_id: uuid.UUID, name: str
    ) -> Watchlist | None:
        result = await self.session.scalars(
            select(Watchlist).where(
                Watchlist.user_id == user_id, Watchlist.name == name
            )
        )
        return result.first()

    async def get_or_create(
        self, user_id: uuid.UUID, name: str
    ) -> tuple[Watchlist, bool]:
        statement = (
            insert(Watchlist)
            .values(user_id=user_id, name=name)
            .on_conflict_do_nothing(constraint="uq_watchlists_user_name")
            .returning(Watchlist.id)
        )
        watchlist_id = (await self.session.execute(statement)).scalar_one_or_none()
        if watchlist_id is not None:
            watchlist = await self.get_by_id(watchlist_id)
            if watchlist is None:
                raise RuntimeError("Created watchlist could not be loaded.")
            return watchlist, True

        watchlist = await self.get_by_user_and_name(user_id, name)
        if watchlist is None:
            raise RuntimeError("Watchlist could not be created or loaded.")
        return watchlist, False


class WatchlistItemRepository(BaseRepository[WatchlistItem]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, WatchlistItem)

    async def list_for_watchlist(
        self,
        watchlist_id: uuid.UUID,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[WatchlistItem]:
        result = await self.session.scalars(
            select(WatchlistItem)
            .where(WatchlistItem.watchlist_id == watchlist_id)
            .offset(offset)
            .limit(limit)
        )
        return list(result.all())

    async def list_with_symbols(
        self, watchlist_id: uuid.UUID
    ) -> list[tuple[WatchlistItem, Symbol]]:
        rows = await self.session.execute(
            select(WatchlistItem, Symbol)
            .join(Symbol, Symbol.id == WatchlistItem.symbol_id)
            .where(WatchlistItem.watchlist_id == watchlist_id)
            .order_by(Symbol.symbol)
        )
        return list(rows.tuples())

    async def add_if_missing(
        self, watchlist_id: uuid.UUID, symbol_id: uuid.UUID
    ) -> tuple[WatchlistItem | None, bool]:
        statement = (
            insert(WatchlistItem)
            .values(watchlist_id=watchlist_id, symbol_id=symbol_id)
            .on_conflict_do_nothing(constraint="uq_watchlist_items_watchlist_symbol")
            .returning(WatchlistItem.id)
        )
        item_id = (await self.session.execute(statement)).scalar_one_or_none()
        if item_id is None:
            return None, False
        return await self.get_by_id(item_id), True

    async def delete_by_symbol_id(
        self, watchlist_id: uuid.UUID, symbol_id: uuid.UUID
    ) -> bool:
        result = await self.session.execute(
            delete(WatchlistItem)
            .where(
                WatchlistItem.watchlist_id == watchlist_id,
                WatchlistItem.symbol_id == symbol_id,
            )
            .returning(WatchlistItem.id)
        )
        return result.scalar_one_or_none() is not None
