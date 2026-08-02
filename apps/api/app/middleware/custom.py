import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.context import request_id_ctx

logger = logging.getLogger("app.access")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that extracts or generates a unique Request ID for tracing."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Set request-scoped state and thread-local/task-local context
        request.state.request_id = request_id
        token = request_id_ctx.set(request_id)

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_ctx.reset(token)


class ProcessingTimeMiddleware(BaseHTTPMiddleware):
    """Middleware that calculates HTTP request processing time."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that applies standard security hardening headers to HTTP responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"

        # Bypass CSP restriction for interactive Swagger / ReDoc docs endpoints
        if not (
            request.url.path.startswith("/docs")
            or request.url.path.startswith("/redoc")
            or request.url.path.endswith("openapi.json")
        ):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; frame-ancestors 'none';"
            )

        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response


class AccessLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that performs request and response logging for access auditing."""

    async def dispatch(self, request: Request, call_next) -> Response:
        client_host = request.client.host if request.client else "unknown"
        request_id_ctx.get()

        logger.info(
            f"Incoming Request: {request.method} {request.url.path} "
            f"from {client_host} (User-Agent: {request.headers.get('user-agent', 'N/A')})"
        )

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time

            logger.info(
                f"Outgoing Response: {request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"Duration: {process_time:.4f}s"
            )
            return response
        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.error(
                f"Request Failed: {request.method} {request.url.path} "
                f"Error: {e!s} "
                f"Duration: {process_time:.4f}s"
            )
            raise e


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware that extracts and sets the active Tenant context (Organization ID) for multi-tenancy."""

    async def dispatch(self, request: Request, call_next) -> Response:
        tenant_header = request.headers.get("X-Tenant-ID")
        tenant_id = None
        if tenant_header:
            try:
                tenant_id = uuid.UUID(tenant_header)
            except ValueError:
                pass

        # Set tenant ID in async context
        from app.core.tenant import set_current_tenant_id

        set_current_tenant_id(tenant_id)

        try:
            response = await call_next(request)
            return response
        finally:
            set_current_tenant_id(None)
