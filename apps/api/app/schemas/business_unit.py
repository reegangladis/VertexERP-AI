from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BusinessUnitBase(BaseModel):
    name: str
    code: str | None = None
    description: str | None = None
    manager_uuid: UUID | None = None
    status: str = "active"


class BusinessUnitCreate(BusinessUnitBase):
    organization_id: UUID
    parent_business_unit_id: UUID | None = None


class BusinessUnitUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None
    manager_uuid: UUID | None = None
    parent_business_unit_id: UUID | None = None
    status: str | None = None


class BusinessUnitResponse(BusinessUnitBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    parent_business_unit_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class BusinessUnitTreeNode(BusinessUnitResponse):
    children: list["BusinessUnitTreeNode"] = []
