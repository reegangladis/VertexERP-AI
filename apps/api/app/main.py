import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.sql import text

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.database.connection import engine
from app.database.redis import get_redis_service
from app.middleware.custom import (
    AccessLoggingMiddleware,
    ProcessingTimeMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
)
from app.middleware.exception_handler import setup_exception_handlers

# Initialize logging configuration
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager handling startup/shutdown routines."""
    # --- STARTUP ---
    logger.info("Initializing application dependencies...")

    # 1. Initialize Redis connection pool
    redis_service = get_redis_service()
    redis_service.initialize()

    # 2. Verify Database connectivity
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database startup healthcheck passed successfully.")
    except Exception as e:
        logger.critical(f"Database connection validation failed during startup: {e}")
        raise RuntimeError(f"Database validation failure: {e}") from e

    # 3. Verify Redis connectivity
    redis_ok = await redis_service.ping()
    if not redis_ok:
        logger.critical("Redis service validation failed during startup.")
        raise RuntimeError(
            "Redis validation failure: Connection could not be established."
        )
    logger.info("Redis startup healthcheck passed successfully.")

    logger.info("All services are operational. Application startup sequence complete.")

    yield

    # --- SHUTDOWN ---
    logger.info("Shutting down application. Releasing resource connections...")

    # Close Redis client
    await redis_service.close()

    # Dispose SQLAlchemy engine connections
    await engine.dispose()

    logger.info("Application shutdown complete.")


# Create the FastAPI instance with enriched OpenAPI details
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "VertexERP AI - Enterprise AI Operating System Backend Foundation API.\n\n"
        "Provides core system abstractions, health audits, unified logging, and standardized responses."
    ),
    version="1.2.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Custom Middlewares (registered innermost first, outermost last)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AccessLoggingMiddleware)
app.add_middleware(ProcessingTimeMiddleware)
app.add_middleware(RequestIDMiddleware)

# Set up CORS middleware (outermost layer wrapping all other custom middlewares)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register exception handlers
setup_exception_handlers(app)

# Include core API routes under version prefix
app.include_router(api_router, prefix=settings.API_V1_STR)
