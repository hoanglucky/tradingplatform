from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.watchlist import Watchlist, WatchlistItem
from app.repositories.base import BaseRepository


class WatchlistRepository(BaseRepository[Watchlist]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Watchlist)

    async def list_for_user(self, user_id: uuid.UUID, *, limit: int = 100, offset: int = 0) -> list[Watchlist]:
        result = await self.session.scalars(
            select(Watchlist).where(Watchlist.user_id == user_id).offset(offset).limit(limit)
        )
        return list(result.all())


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
            select(WatchlistItem).where(WatchlistItem.watchlist_id == watchlist_id).offset(offset).limit(limit)
        )
        return list(result.all())
