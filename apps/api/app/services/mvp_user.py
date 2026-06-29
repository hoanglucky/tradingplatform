from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.users import UserRepository


async def ensure_mvp_user(session: AsyncSession) -> tuple[User, bool]:
    email = settings.mvp_user_email.strip().lower()
    display_name = settings.mvp_user_display_name.strip()
    return await UserRepository(session).get_or_create_by_email(email, display_name)


async def get_mvp_user(db: AsyncSession = Depends(get_db)) -> User:
    if not settings.mvp_user_mode:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MVP user mode is disabled and authentication is not configured.",
        )

    user, created = await ensure_mvp_user(db)
    if created:
        await db.commit()
        await db.refresh(user)
    return user
