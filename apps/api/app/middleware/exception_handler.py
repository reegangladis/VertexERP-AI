import logging

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """Configures global error interceptors for the FastAPI app."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Intercepts HTTPExceptions and formats standard error response."""
        logger.warning(f"HTTP error occurred on {request.url.path}: {exc.detail}")
        # If exc.detail is already a dict, we can keep it as is, otherwise wrap it
        detail = (
            exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder({"error": detail}),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Intercepts Pydantic model validation errors."""
        logger.error(f"Validation error on {request.url.path}: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder(
                {
                    "error": {
                        "message": "Validation failed for request parameters",
                        "details": exc.errors(),
                    }
                }
            ),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Catch-all handler for unhandled internal code errors (500)."""
        logger.exception(f"Unhandled system error occurred on {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                {
                    "error": {
                        "message": "An internal system error occurred. Please contact support.",
                        "details": str(exc) if settings_is_dev() else None,
                    }
                }
            ),
        )


def settings_is_dev() -> bool:
    """Helper to check if settings is loaded and is in development environment."""
    try:
        from app.core.config import settings

        return settings.ENVIRONMENT == "development"
    except Exception:
        return True
