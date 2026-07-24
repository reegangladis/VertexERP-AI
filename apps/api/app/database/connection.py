from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Create async engine for PostgreSQL
engine = create_async_engine(
    settings.database_url_async,
    pool_pre_ping=True,
    future=True,
    echo=False,
    pool_size=settings.POSTGRES_POOL_SIZE,
    max_overflow=settings.POSTGRES_MAX_OVERFLOW,
)

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
