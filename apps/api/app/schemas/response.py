from datetime import UTC, datetime
from typing import Any, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse[T](BaseModel):
    """Standardized API response container matching enterprise guidelines."""

    success: bool = Field(..., description="Flag indicating operation success")
    message: str = Field("", description="Human-readable response message")
    data: T | None = Field(None, description="Response payload")
    meta: dict[str, Any] = Field(default_factory=dict, description="Metadata envelope")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO 8601 UTC timestamp",
    )
