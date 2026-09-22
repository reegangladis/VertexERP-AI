"""Cost Center schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CostCenterBase(BaseModel):
    """Base fields for cost center."""

    code: str = Field(..., min_length=1, max_length=32, description="Unique cost center code")
    name: str = Field(..., min_length=1, max_length=128, description="Cost center name")
    description: str | None = Field(None, description="Cost center description")
    department_id: uuid.UUID | None = Field(None, description="Linked Department ID")
    annual_budget: Decimal = Field(
        default=Decimal("0.0000"), ge=0, description="Annual budget allocation"
    )
    currency: str = Field(
        default="USD", min_length=3, max_length=3, description="3-letter currency code"
    )
    is_active: bool = True


class CostCenterCreate(CostCenterBase):
    """Schema for creating cost center."""

    pass


class CostCenterUpdate(BaseModel):
    """Schema for updating cost center."""

    code: str | None = Field(None, min_length=1, max_length=32)
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None
    department_id: uuid.UUID | None = None
    annual_budget: Decimal | None = Field(None, ge=0)
    currency: str | None = Field(None, min_length=3, max_length=3)
    is_active: bool | None = None


class CostCenterResponse(CostCenterBase):
    """Response schema for cost center."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
