from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User
from app.models.watchlist import Watchlist
from app.repositories.watchlists import WatchlistRepository


async def ensure_default_watchlist(
    session: AsyncSession, user: User
) -> tuple[Watchlist, bool]:
    name = settings.mvp_watchlist_name.strip()
    return await WatchlistRepository(session).get_or_create(user.id, name)
