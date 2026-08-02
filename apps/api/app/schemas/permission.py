import uuid

from pydantic import BaseModel, Field


class PermissionCreate(BaseModel):
    name: str = Field(..., min_length=2)
    description: str | None = None
    category: str = "default"


class PermissionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None


class PermissionResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    category: str

    class Config:
        from_attributes = True
