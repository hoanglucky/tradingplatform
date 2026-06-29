from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.scalars(select(User).where(User.email == email))
        return result.first()

    async def get_or_create_by_email(
        self, email: str, display_name: str | None = None
    ) -> tuple[User, bool]:
        statement = (
            insert(User)
            .values(email=email, display_name=display_name)
            .on_conflict_do_nothing(index_elements=[User.email])
            .returning(User.id)
        )
        user_id = (await self.session.execute(statement)).scalar_one_or_none()
        if user_id is not None:
            user = await self.get_by_id(user_id)
            if user is None:
                raise RuntimeError("Created MVP user could not be loaded.")
            return user, True

        user = await self.get_by_email(email)
        if user is None:
            raise RuntimeError("MVP user could not be created or loaded.")
        return user, False
