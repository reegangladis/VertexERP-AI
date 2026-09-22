"""Async SQLAlchemy database session management and health monitoring."""

import time
import uuid
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.constants import ServiceStatus
from app.core.context import get_tenant_id
from app.core.logging import logger
from app.core.metrics import metrics_registry

# Global async engine and sessionmaker instances
engine: AsyncEngine = create_async_engine(
    settings.async_database_url,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
)

async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def _is_postgresql(session: AsyncSession) -> bool:
    """Helper to determine if the active session is bound to a PostgreSQL engine."""
    bind = session.bind or (session.sync_session.get_bind() if hasattr(session, "sync_session") else None)
    if bind and hasattr(bind, "dialect"):
        return bind.dialect.name == "postgresql"
    return True


async def set_tenant_context(session: AsyncSession, tenant_id: uuid.UUID | str | None) -> None:
    """
    Establishes transaction-local PostgreSQL RLS context safely using set_config.
    When executed against non-PostgreSQL dialects (e.g. SQLite in test suites),
    this operation is safely bypassed.
    """
    if not tenant_id:
        return
    if not _is_postgresql(session):
        return

    await session.execute(
        text("SELECT set_config('app.current_tenant_id', :tenant_id, true)"),
        {"tenant_id": str(tenant_id)},
    )


async def set_superuser_context(session: AsyncSession, is_superuser: bool = True) -> None:
    """
    Sets transaction-local superuser bypass flag for controlled administrative
    and bootstrap operations before scoping to a tenant.
    """
    if not _is_postgresql(session):
        return

    await session.execute(
        text("SELECT set_config('app.is_superuser', :is_superuser, true)"),
        {"is_superuser": "true" if is_superuser else "false"},
    )


def sync_db_pool_metrics() -> None:
    """Updates database connection pool telemetry gauges."""
    try:
        if hasattr(engine, "sync_engine") and hasattr(engine.sync_engine, "pool"):
            pool = engine.sync_engine.pool
            if hasattr(pool, "size"):
                metrics_registry.db_pool_size.set(pool.size())
            if hasattr(pool, "checkedout"):
                metrics_registry.db_pool_checked_out.set(pool.checkedout())
            if hasattr(pool, "overflow"):
                metrics_registry.db_pool_overflow.set(pool.overflow())
    except Exception:
        pass


async def init_db_engine() -> None:
    """Initializes the database connection pool during application startup."""
    logger.info(
        "Initializing PostgreSQL connection pool",
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        database=settings.DATABASE_NAME,
        pool_size=settings.DATABASE_POOL_SIZE,
    )
    sync_db_pool_metrics()


async def close_db_engine() -> None:
    """Disposes the database connection pool during application shutdown."""
    logger.info("Closing PostgreSQL connection pool")
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency yielding an isolated AsyncSession bound to a transaction.
    Automatically sets the PostgreSQL RLS session variable if a tenant context exists.
    """
    sync_db_pool_metrics()
    async with async_session_factory() as session:
        tenant_id = get_tenant_id()
        if tenant_id:
            await set_tenant_context(session, tenant_id)
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            sync_db_pool_metrics()


async def check_db_health() -> dict[str, object]:
    """Executes a ping query to assess database responsiveness and latency."""
    sync_db_pool_metrics()
    start_time = time.perf_counter()
    try:
        async with async_session_factory() as session:
            result = await session.execute(text("SELECT 1"))
            val = result.scalar()
            latency = time.perf_counter() - start_time
            latency_ms = round(latency * 1000, 2)
            metrics_registry.db_query_duration_seconds.observe(
                latency, labels={"operation": "ping", "table": "none"}
            )
            if val == 1:
                return {
                    "status": ServiceStatus.HEALTHY.value,
                    "latency_ms": latency_ms,
                    "message": "PostgreSQL database is operational",
                }
            return {
                "status": ServiceStatus.UNHEALTHY.value,
                "latency_ms": latency_ms,
                "message": f"Unexpected ping response: {val}",
            }
    except Exception as exc:
        latency = time.perf_counter() - start_time
        latency_ms = round(latency * 1000, 2)
        metrics_registry.db_query_errors_total.inc(
            labels={"operation": "ping", "error_type": exc.__class__.__name__}
        )
        logger.error("PostgreSQL health check failed", error=str(exc), latency_ms=latency_ms)
        return {
            "status": ServiceStatus.UNHEALTHY.value,
            "latency_ms": latency_ms,
            "error": str(exc),
        }
