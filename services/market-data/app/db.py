from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import settings

engine_options = {"pool_pre_ping": True}
if settings.app_env == "test":
    engine_options["poolclass"] = NullPool

engine = create_async_engine(settings.database_url, **engine_options)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
