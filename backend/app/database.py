from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.config import settings


# Async engine for FastAPI
engine = create_async_engine(
	settings.DATABASE_URL,
	pool_size=5,
	max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
	bind=engine,
	class_=AsyncSession,
	expire_on_commit=False,
)

# Sync engine for Celery workers (not async)
sync_engine = create_engine(
	settings.DATABASE_URL.replace("+asyncpg", ""),
	pool_size=5,
	max_overflow=10,
)

sync_sessionmaker = sessionmaker(
	bind=sync_engine,
	class_=Session,
	expire_on_commit=False,
)


class Base(DeclarativeBase):
	pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
	async with AsyncSessionLocal() as session:
		try:
			yield session
			await session.commit()
		except Exception:
			await session.rollback()
			raise
		finally:
			await session.close()