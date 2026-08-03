from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LocationBase(BaseModel):
    country: str | None = None
    state: str | None = None
    city: str | None = None
    address: str | None = None
    zipcode: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class LocationCreate(LocationBase):
    organization_id: UUID


class LocationUpdate(BaseModel):
    country: str | None = None
    state: str | None = None
    city: str | None = None
    address: str | None = None
    zipcode: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class LocationResponse(LocationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
