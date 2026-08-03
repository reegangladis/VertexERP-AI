from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DepartmentBase(BaseModel):
    name: str
    code: str | None = None
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    manager_uuid: UUID | None = None
    budget: float = 0.0
    cost_center: str | None = None
    status: str = "active"


class DepartmentCreate(DepartmentBase):
    organization_id: UUID
    parent_department_id: UUID | None = None


class DepartmentUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None
    email: str | None = None
    phone: str | None = None
    manager_uuid: UUID | None = None
    parent_department_id: UUID | None = None
    budget: float | None = None
    cost_center: str | None = None
    status: str | None = None


class DepartmentResponse(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    parent_department_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class DepartmentTreeNode(DepartmentResponse):
    children: list["DepartmentTreeNode"] = []
