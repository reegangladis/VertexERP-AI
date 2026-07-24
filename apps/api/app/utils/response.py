from datetime import UTC, datetime
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def build_response(
    success: bool,
    message: str = "",
    data: Any = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Builds a standardized dictionary response payload."""
    return {
        "success": success,
        "message": message,
        "data": data,
        "meta": meta or {},
        "timestamp": datetime.now(UTC).isoformat(),
    }


def standard_response(
    data: Any = None, message: str = "", meta: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Convenience helper for building success response dictionaries."""
    return build_response(success=True, message=message, data=data, meta=meta)


def standard_json_response(
    status_code: int,
    success: bool,
    message: str = "",
    data: Any = None,
    meta: dict[str, Any] | None = None,
) -> JSONResponse:
    """Builds and returns a standardized FastAPI JSONResponse."""
    payload = build_response(success=success, message=message, data=data, meta=meta)
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(payload),
    )
