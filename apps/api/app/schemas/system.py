from datetime import datetime

from pydantic import BaseModel, Field


class VersionResponse(BaseModel):
    """Pydantic schema representing the API version response."""

    status: str = Field(..., description="Overall system status")
    version: str = Field(..., description="Current application version")
    environment: str = Field(..., description="Runtime environment name")
    timestamp: datetime = Field(
        ..., description="Server timestamp of response generation"
    )


class HealthResponse(BaseModel):
    """Pydantic schema representing the detailed system health response."""

    status: str = Field(..., description="Overall health state (e.g. green, red)")
    version: str = Field(..., description="Current application version")
    environment: str = Field(..., description="Runtime environment name")
    timestamp: datetime = Field(
        ..., description="Server timestamp of response generation"
    )
    services: dict[str, str] = Field(
        ..., description="Detailed status of external components"
    )
