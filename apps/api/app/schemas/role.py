import uuid

from pydantic import BaseModel, Field


class PermissionSummary(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    category: str

    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    organization_id: uuid.UUID | None = None
    permissions: list[PermissionSummary] = []

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=2)
    description: str | None = None


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class RoleAssignPermissions(BaseModel):
    permissions: list[str]
