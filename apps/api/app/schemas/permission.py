from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PermissionBase(BaseModel):
    code: str
    module: str = "core"
    description: str | None = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    code: str | None = None
    module: str | None = None
    description: str | None = None


class PermissionResponse(PermissionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
