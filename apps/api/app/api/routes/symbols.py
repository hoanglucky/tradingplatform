from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.symbols import SymbolRepository
from app.schemas.symbol import SymbolCreate, SymbolRead, SymbolUpdate

router = APIRouter()


def duplicate_symbol_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Symbol already exists for this exchange.",
    )


@router.get("", response_model=list[SymbolRead])
async def list_symbols(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
) -> list[SymbolRead]:
    repo = SymbolRepository(db)
    if active_only:
        return await repo.list_active(limit=limit, offset=offset)
    return await repo.list(limit=limit, offset=offset)


@router.get("/{symbol_id}", response_model=SymbolRead)
async def get_symbol(symbol_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> SymbolRead:
    repo = SymbolRepository(db)
    symbol = await repo.get_by_id(symbol_id)
    if symbol is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found.")
    return symbol


@router.post("", response_model=SymbolRead, status_code=status.HTTP_201_CREATED)
async def create_symbol(payload: SymbolCreate, db: AsyncSession = Depends(get_db)) -> SymbolRead:
    repo = SymbolRepository(db)
    existing = await repo.get_by_symbol(payload.exchange, payload.symbol)
    if existing is not None:
        raise duplicate_symbol_error()

    try:
        symbol = await repo.create(**payload.model_dump())
        await db.commit()
        await db.refresh(symbol)
    except IntegrityError as exc:
        await db.rollback()
        raise duplicate_symbol_error() from exc

    return symbol


@router.patch("/{symbol_id}", response_model=SymbolRead)
async def update_symbol(
    symbol_id: uuid.UUID,
    payload: SymbolUpdate,
    db: AsyncSession = Depends(get_db),
) -> SymbolRead:
    values = payload.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No symbol fields provided.")

    repo = SymbolRepository(db)
    try:
        symbol = await repo.update(symbol_id, **values)
        if symbol is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found.")
        await db.commit()
        await db.refresh(symbol)
    except IntegrityError as exc:
        await db.rollback()
        raise duplicate_symbol_error() from exc

    return symbol


@router.delete("/{symbol_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_symbol(symbol_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Response:
    repo = SymbolRepository(db)
    deleted = await repo.delete(symbol_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found.")

    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
