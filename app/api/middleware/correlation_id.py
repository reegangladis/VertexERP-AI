"""Correlation ID Middleware for distributed end-to-end request tracing."""

import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.constants import HEADER_CORRELATION_ID
from app.core.context import set_correlation_id

HEADER_REQUEST_ID = "X-Request-ID"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Extracts or generates a correlation ID for every incoming request.
    Populates the contextvar, binds to structlog, and attaches headers to the response.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Extract from headers (supporting X-Correlation-ID, X-Request-ID, Request-ID)
        correlation_id = (
            request.headers.get(HEADER_CORRELATION_ID)
            or request.headers.get(HEADER_REQUEST_ID)
            or request.headers.get("Request-ID")
        )
        if not correlation_id:
            correlation_id = f"req_{uuid.uuid4().hex}"

        # Propagate to contextvar and structlog
        set_correlation_id(correlation_id)
        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id,
            path=str(request.url.path),
            method=request.method,
        )

        # Execute downstream pipeline
        response = await call_next(request)

        # Inject into outgoing HTTP response headers
        response.headers[HEADER_CORRELATION_ID] = correlation_id
        response.headers[HEADER_REQUEST_ID] = correlation_id
        return response
