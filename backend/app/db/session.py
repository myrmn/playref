"""Database session and connection management."""

from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.config import settings
from backend.app.db.models import Base
from backend.app.logger import logger

_engine = None
_session_maker = None


async def get_engine():
    global _engine, _session_maker
    if _engine is not None:
        return _engine

    db_url = settings.database_url
    try:
        engine = create_async_engine(db_url, echo=False)
        # Test connection
        async with engine.connect() as conn:
            await conn.run_sync(lambda _: None)
        logger.info(f"Connected to primary database: {db_url}")
        _engine = engine
    except Exception as exc:
        fallback_path = Path("data/playref.db")
        fallback_path.parent.mkdir(parents=True, exist_ok=True)
        sqlite_url = f"sqlite+aiosqlite:///{fallback_path}"
        logger.warning(
            f"Primary database ({db_url}) unreachable ({exc}); falling back to local SQLite at {sqlite_url}"
        )
        _engine = create_async_engine(sqlite_url, echo=False)

    # Initialize tables
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    _session_maker = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)
    return _engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding database session."""
    global _session_maker
    if _session_maker is None:
        await get_engine()
    async with _session_maker() as session:
        yield session
