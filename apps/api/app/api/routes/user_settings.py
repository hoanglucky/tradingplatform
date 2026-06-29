from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.models.user_settings import UserSettings
from app.repositories.symbols import SymbolRepository
from app.repositories.user_settings import UserSettingsRepository
from app.schemas.user_settings import UserSettingsPatch, UserSettingsRead
from app.services.mvp_user import get_mvp_user

router = APIRouter()


async def ensure_user_settings(
    db: AsyncSession, user: User
) -> tuple[UserSettings, bool]:
    return await UserSettingsRepository(db).get_or_create(user.id)


@router.get("", response_model=UserSettingsRead)
async def get_settings(
    user: User = Depends(get_mvp_user),
    db: AsyncSession = Depends(get_db),
) -> UserSettings:
    user_settings, created = await ensure_user_settings(db, user)
    if created:
        await db.commit()
        await db.refresh(user_settings)
    return user_settings


@router.patch("", response_model=UserSettingsRead)
async def patch_settings(
    payload: UserSettingsPatch,
    user: User = Depends(get_mvp_user),
    db: AsyncSession = Depends(get_db),
) -> UserSettings:
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    default_symbol = changes.get("default_symbol")
    if default_symbol is not None:
        symbol = await SymbolRepository(db).get_active_by_symbol(default_symbol)
        if symbol is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active default symbol not found.",
            )

    user_settings, _ = await ensure_user_settings(db, user)
    for key, value in changes.items():
        setattr(user_settings, key, value)
    await db.commit()
    await db.refresh(user_settings)
    return user_settings
