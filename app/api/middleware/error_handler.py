"""Global Exception Handling Middleware enforcing IETF RFC 7807 Problem Details and Error Tracking."""

from datetime import UTC, datetime
from typing import Any

from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings
from app.core.constants import HEADER_CORRELATION_ID, MEDIA_TYPE_PROBLEM_JSON, Environment
from app.core.context import get_correlation_id
from app.core.error_tracker import error_tracker
from app.core.exceptions import AppException
from app.core.logging import logger


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Catches domain AppExceptions, validation errors, and uncaught exceptions.
    Serializes errors into standardized RFC 7807 Problem Details JSON format and records telemetry.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except AppException as exc:
            return self._handle_app_exception(request, exc)
        except RequestValidationError as exc:
            return self._handle_validation_error(request, exc)
        except Exception as exc:
            return self._handle_uncaught_exception(request, exc)

    def _handle_app_exception(self, request: Request, exc: AppException) -> JSONResponse:
        correlation_id = get_correlation_id() or "unknown"
        fingerprint = error_tracker.record_error(
            exc=exc,
            path=str(request.url.path),
            status_code=exc.status_code,
            correlation_id=correlation_id,
        )

        logger.warning(
            "Application domain exception intercepted",
            status_code=exc.status_code,
            title=exc.title,
            detail=exc.detail,
            path=str(request.url.path),
            correlation_id=correlation_id,
            fingerprint=fingerprint,
        )
        content: dict[str, Any] = {
            "type": exc.error_type,
            "title": exc.title,
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": str(request.url.path),
            "correlation_id": correlation_id,
            "error_fingerprint": fingerprint,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        if exc.invalid_params:
            content["invalid_params"] = exc.invalid_params

        headers = {
            HEADER_CORRELATION_ID: correlation_id,
            "X-Request-ID": correlation_id,
            "X-Error-Fingerprint": fingerprint,
            **exc.headers,
        }
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers=headers,
            media_type=MEDIA_TYPE_PROBLEM_JSON,
        )

    def _handle_validation_error(
        self, request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        correlation_id = get_correlation_id() or "unknown"
        fingerprint = error_tracker.record_error(
            exc=exc,
            path=str(request.url.path),
            status_code=422,
            correlation_id=correlation_id,
        )

        invalid_params = []
        for error in exc.errors():
            loc = ".".join(str(x) for x in error.get("loc", []))
            invalid_params.append(
                {
                    "field": loc,
                    "reason": error.get("msg", "Invalid value"),
                    "type": error.get("type", "value_error"),
                }
            )

        logger.info(
            "Request validation failure",
            invalid_params=invalid_params,
            path=str(request.url.path),
            correlation_id=correlation_id,
            fingerprint=fingerprint,
        )
        content: dict[str, Any] = {
            "type": "https://api.vertexerp.io/errors/validation-error",
            "title": "Unprocessable Entity",
            "status": 422,
            "detail": "Request payload failed schema validation rules.",
            "instance": str(request.url.path),
            "correlation_id": correlation_id,
            "error_fingerprint": fingerprint,
            "timestamp": datetime.now(UTC).isoformat(),
            "invalid_params": invalid_params,
        }
        return JSONResponse(
            status_code=422,
            content=content,
            headers={
                HEADER_CORRELATION_ID: correlation_id,
                "X-Request-ID": correlation_id,
                "X-Error-Fingerprint": fingerprint,
            },
            media_type=MEDIA_TYPE_PROBLEM_JSON,
        )

    def _handle_uncaught_exception(self, request: Request, exc: Exception) -> JSONResponse:
        correlation_id = get_correlation_id() or "unknown"
        fingerprint = error_tracker.record_error(
            exc=exc,
            path=str(request.url.path),
            status_code=500,
            correlation_id=correlation_id,
        )

        logger.error(
            "Unhandled critical server exception",
            error=str(exc),
            path=str(request.url.path),
            correlation_id=correlation_id,
            fingerprint=fingerprint,
            exc_info=True,
        )
        detail = "An unexpected error occurred. Please provide the correlation ID to support."
        if settings.DEBUG and settings.APP_ENV == Environment.DEVELOPMENT:
            detail = f"{detail} (Debug: {type(exc).__name__}: {str(exc)})"

        content: dict[str, Any] = {
            "type": "https://api.vertexerp.io/errors/internal-server-error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": detail,
            "instance": str(request.url.path),
            "correlation_id": correlation_id,
            "error_fingerprint": fingerprint,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return JSONResponse(
            status_code=500,
            content=content,
            headers={
                HEADER_CORRELATION_ID: correlation_id,
                "X-Request-ID": correlation_id,
                "X-Error-Fingerprint": fingerprint,
            },
            media_type=MEDIA_TYPE_PROBLEM_JSON,
        )
