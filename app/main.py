import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.middleware.correlation_id import CorrelationIdMiddleware
from app.api.middleware.error_handler import ErrorHandlerMiddleware
from app.api.middleware.metrics_middleware import MetricsMiddleware
from app.api.middleware.rate_limiter import RateLimitMiddleware
from app.api.middleware.security_headers import SecurityHeadersMiddleware
from app.api.v1.health import router as root_health_router
from app.api.v1.metrics import router as root_metrics_router
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.infrastructure.database.session import close_db_engine, init_db_engine
from app.infrastructure.redis.client import close_redis_client, init_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application lifecycle: logging, database pool, redis, and optional embedded worker."""
    # 1. Startup Phase
    setup_logging()
    logger.info(
        "Starting VertexERP AI V2 Application Engine",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV.value,
        deployment_mode=settings.DEPLOYMENT_MODE,
    )
    await init_db_engine()
    await init_redis_client()

    # 2. Embedded Worker Initialization (Used in Free Deployment Mode)
    embedded_worker_pool = None
    scheduler_task = None
    should_run_embedded_worker = (
        settings.WORKER_MODE.lower() == "embedded"
        or (
            settings.WORKER_MODE.lower() == "auto"
            and (
                settings.DEPLOYMENT_MODE.lower() == "free"
                or settings.APP_ENV.value == "free"
            )
        )
    )

    if should_run_embedded_worker:
        logger.info("Initializing embedded Background Worker Pool for free/lightweight deployment mode")
        from app.infrastructure.database.session import async_session_factory
        from app.modules.jobs.engine.job_queue import job_queue_manager
        from app.modules.jobs.engine.scheduler import CronScheduler
        from app.modules.jobs.engine.worker_pool import worker_pool

        worker_pool.configure(
            session_factory=async_session_factory,
            concurrency=2,
        )
        await worker_pool.start()
        embedded_worker_pool = worker_pool

        async def _embedded_scheduler_loop() -> None:
            while True:
                try:
                    await asyncio.sleep(60.0)
                    async with async_session_factory() as session:
                        async with session.begin():
                            triggered = await CronScheduler.evaluate_schedules(session)
                        if triggered:
                            for job in triggered:
                                await job_queue_manager.enqueue(
                                    job.id,
                                    priority=job.priority,
                                    scheduled_at=job.scheduled_at,
                                )
                            logger.info("Embedded CronScheduler triggered %d recurring jobs", len(triggered))
                except asyncio.CancelledError:
                    break
                except Exception as exc:
                    logger.warning("Error in embedded CronScheduler loop: %s", exc)

        scheduler_task = asyncio.create_task(_embedded_scheduler_loop())

    yield

    # 3. Shutdown Phase
    logger.info("Initiating graceful shutdown sequence")
    if scheduler_task:
        scheduler_task.cancel()
        with suppress(asyncio.CancelledError):
            await scheduler_task

    if embedded_worker_pool:
        logger.info("Stopping embedded Background Worker Pool")
        await embedded_worker_pool.stop()

    await close_redis_client()
    await close_db_engine()
    logger.info("VertexERP AI V2 Application Engine stopped")


def create_app() -> FastAPI:
    """FastAPI Application Factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="VertexERP AI V2 - Enterprise Multi-Tenant ERP Platform with AI Gateway",
        docs_url="/docs" if settings.DEBUG or settings.APP_ENV.value != "production" else None,
        redoc_url="/redoc" if settings.DEBUG or settings.APP_ENV.value != "production" else None,
        openapi_url="/openapi.json"
        if settings.DEBUG or settings.APP_ENV.value != "production"
        else None,
        lifespan=lifespan,
    )

    # --------------------------------------------------------------------------
    # Middleware Stack (Ordered from Outermost to Innermost)
    # --------------------------------------------------------------------------
    # 1. Error Handler: Catches all exceptions and outputs RFC 7807 Problem Details
    app.add_middleware(ErrorHandlerMiddleware)

    # 2. Security Headers: Injects HSTS, X-Content-Type-Options, CSP, etc.
    app.add_middleware(SecurityHeadersMiddleware)

    # 3. Rate Limiter: Redis-backed sliding window rate limit defense
    app.add_middleware(RateLimitMiddleware)

    # 4. Correlation ID: Injects X-Correlation-ID and X-Request-ID for distributed tracing
    app.add_middleware(CorrelationIdMiddleware)

    # 5. Metrics Middleware: Tracks HTTP request counts, latency histograms, in-flight gauges
    app.add_middleware(MetricsMiddleware)

    # 6. CORS Middleware: Strict origin whitelist (No wildcard in production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=[
            "X-Correlation-ID",
            "X-Request-ID",
            "X-Error-Fingerprint",
            "Content-Disposition",
        ],
        max_age=3600,
    )

    # 7. Trusted Host Middleware: Protects against HTTP Host header attacks
    if settings.ALLOWED_HOSTS:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )

    # --------------------------------------------------------------------------
    # Route Registration
    # --------------------------------------------------------------------------
    # Root Health Endpoints (for Kubernetes standard probes: /health/live, /health/ready)
    app.include_router(root_health_router)

    # Root Metrics Endpoints (/metrics, /metrics/json)
    app.include_router(root_metrics_router)

    # Versioned API Router (/api/v1/...)
    app.include_router(api_v1_router)

    @app.get("/", tags=["Root"], summary="Application Index")
    async def root() -> dict[str, str]:
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "OPERATIONAL",
            "docs": "/docs" if app.docs_url else "Disabled in production",
            "metrics": "/metrics",
        }

    return app


# Root ASGI application instance
app = create_app()
