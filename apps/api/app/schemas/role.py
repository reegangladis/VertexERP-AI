from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.permission import PermissionResponse


class RoleBase(BaseModel):
    name: str
    description: str | None = None
    is_system: bool = False


class RoleCreate(RoleBase):
    organization_id: UUID | None = None
    permission_ids: list[UUID] = []


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    permission_ids: list[UUID] | None = None


class RoleResponse(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID | None = None
    permissions: list[PermissionResponse] = []
    created_at: datetime
    updated_at: datetime
