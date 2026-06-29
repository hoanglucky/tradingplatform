from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.symbol import Symbol
from app.models.user import User
from app.models.watchlist import Watchlist, WatchlistItem
from app.repositories.symbols import SymbolRepository
from app.repositories.watchlists import WatchlistItemRepository
from app.schemas.watchlist import WatchlistItemCreate, WatchlistItemRead, WatchlistRead
from app.services.mvp_user import get_mvp_user
from app.services.watchlist import ensure_default_watchlist

router = APIRouter()


def item_response(item: WatchlistItem, symbol: Symbol) -> WatchlistItemRead:
    return WatchlistItemRead(
        id=item.id,
        symbol_id=symbol.id,
        exchange=symbol.exchange,
        symbol=symbol.symbol,
        base_asset=symbol.base_asset,
        quote_asset=symbol.quote_asset,
        created_at=item.created_at,
    )


async def watchlist_response(db: AsyncSession, watchlist: Watchlist) -> WatchlistRead:
    rows = await WatchlistItemRepository(db).list_with_symbols(watchlist.id)
    return WatchlistRead(
        id=watchlist.id,
        user_id=watchlist.user_id,
        name=watchlist.name,
        items=[item_response(item, symbol) for item, symbol in rows],
    )


@router.get("", response_model=WatchlistRead)
async def get_watchlist(
    user: User = Depends(get_mvp_user),
    db: AsyncSession = Depends(get_db),
) -> WatchlistRead:
    watchlist, created = await ensure_default_watchlist(db, user)
    if created:
        await db.commit()
        await db.refresh(watchlist)
    return await watchlist_response(db, watchlist)


@router.post(
    "/items", response_model=WatchlistItemRead, status_code=status.HTTP_201_CREATED
)
async def add_watchlist_item(
    payload: WatchlistItemCreate,
    user: User = Depends(get_mvp_user),
    db: AsyncSession = Depends(get_db),
) -> WatchlistItemRead:
    symbol = await SymbolRepository(db).get_active_by_symbol(payload.symbol)
    if symbol is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Active symbol not found."
        )

    watchlist, _ = await ensure_default_watchlist(db, user)
    item, created = await WatchlistItemRepository(db).add_if_missing(
        watchlist.id, symbol.id
    )
    if not created or item is None:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Symbol already exists in watchlist.",
        )

    await db.commit()
    await db.refresh(item)
    return item_response(item, symbol)


@router.delete("/items/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist_item(
    symbol: str,
    user: User = Depends(get_mvp_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    normalized_symbol = symbol.strip().upper()
    market_symbol = await SymbolRepository(db).get_active_by_symbol(normalized_symbol)
    if market_symbol is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Active symbol not found."
        )

    watchlist, _ = await ensure_default_watchlist(db, user)
    deleted = await WatchlistItemRepository(db).delete_by_symbol_id(
        watchlist.id, market_symbol.id
    )
    if not deleted:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist item not found."
        )

    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
