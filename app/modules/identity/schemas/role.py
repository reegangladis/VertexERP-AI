"""Pydantic schemas for Role, Permission, and RBAC assignment."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    domain: str
    resource: str
    action: str
    description: str


class RoleCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=64)
    code: str = Field(..., min_length=2, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    description: str | None = None
    permission_ids: list[uuid.UUID] = Field(default_factory=list)


class RoleUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=64)
    description: str | None = None
    permission_ids: list[uuid.UUID] | None = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    code: str
    description: str | None
    is_system_role: bool
    created_at: datetime
    permissions: list[PermissionResponse] = Field(default_factory=list)


class AssignRoleRequest(BaseModel):
    user_id: uuid.UUID
    role_id: uuid.UUID
    organization_id: uuid.UUID
    branch_id: uuid.UUID | None = None
    department_id: uuid.UUID | None = None
