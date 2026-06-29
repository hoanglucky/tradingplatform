from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_settings import UserSettings
from app.repositories.base import BaseRepository


class UserSettingsRepository(BaseRepository[UserSettings]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserSettings)

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserSettings | None:
        return await self.session.scalar(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )

    async def get_or_create(self, user_id: uuid.UUID) -> tuple[UserSettings, bool]:
        statement = (
            insert(UserSettings)
            .values(user_id=user_id)
            .on_conflict_do_nothing(index_elements=[UserSettings.user_id])
            .returning(UserSettings.id)
        )
        settings_id = (await self.session.execute(statement)).scalar_one_or_none()
        if settings_id is not None:
            created = await self.get_by_id(settings_id)
            if created is None:
                raise RuntimeError("Created user settings could not be loaded.")
            return created, True

        existing = await self.get_by_user_id(user_id)
        if existing is None:
            raise RuntimeError("User settings could not be created or loaded.")
        return existing, False
