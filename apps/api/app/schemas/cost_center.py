from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CostCenterBase(BaseModel):
    code: str
    name: str
    description: str | None = None
    status: str = "active"


class CostCenterCreate(CostCenterBase):
    organization_id: UUID
    department_id: UUID | None = None


class CostCenterUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    description: str | None = None
    department_id: UUID | None = None
    status: str | None = None


class CostCenterResponse(CostCenterBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    department_id: UUID | None = None
    created_at: datetime
    updated_at: datetime
