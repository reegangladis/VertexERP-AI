"""Department schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DepartmentBase(BaseModel):
    """Base fields for department."""

    code: str = Field(..., min_length=1, max_length=32, description="Unique department code")
    name: str = Field(..., min_length=1, max_length=128, description="Department name")
    description: str | None = Field(None, description="Detailed description")
    parent_department_id: uuid.UUID | None = Field(
        None, description="Parent department ID for hierarchy"
    )
    manager_user_id: uuid.UUID | None = Field(None, description="Manager user ID")
    is_active: bool = True


class DepartmentCreate(DepartmentBase):
    """Schema for creating department."""

    pass


class DepartmentUpdate(BaseModel):
    """Schema for updating department."""

    code: str | None = Field(None, min_length=1, max_length=32)
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None
    parent_department_id: uuid.UUID | None = None
    manager_user_id: uuid.UUID | None = None
    is_active: bool | None = None


class DepartmentResponse(DepartmentBase):
    """Response schema for department."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DepartmentTreeNode(DepartmentResponse):
    """Hierarchical department tree node."""

    children: list["DepartmentTreeNode"] = []
