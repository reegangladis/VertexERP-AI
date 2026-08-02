import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

logger = logging.getLogger(__name__)


def create_db_engine() -> AsyncEngine:
    """Creates appropriate AsyncEngine for PostgreSQL or SQLite fallback."""
    db_url = getattr(settings, "DATABASE_URL", None)
    if db_url and db_url.startswith("sqlite"):
        return create_async_engine(db_url, future=True, echo=False)

    try:
        return create_async_engine(
            settings.database_url_async,
            pool_pre_ping=True,
            future=True,
            echo=False,
            pool_size=settings.POSTGRES_POOL_SIZE,
            max_overflow=settings.POSTGRES_MAX_OVERFLOW,
        )
    except Exception as e:
        logger.warning(
            f"PostgreSQL engine creation warning: {e}. Defaulting to SQLite fallback."
        )
        return create_async_engine(
            "sqlite+aiosqlite:///./vertexerp.db", future=True, echo=False
        )


engine = create_db_engine()


def set_fallback_sqlite_engine() -> None:
    """Switches the global database engine to local SQLite when PostgreSQL is offline."""
    global engine, async_session_maker
    logger.info("Initializing standalone SQLite database engine (vertexerp.db)")
    engine = create_async_engine(
        "sqlite+aiosqlite:///./vertexerp.db", future=True, echo=False
    )
    async_session_maker.configure(bind=engine)


# Async session maker
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Dependency for obtaining an asynchronous database session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
