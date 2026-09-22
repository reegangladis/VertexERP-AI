"""Pydantic Schemas for Bills of Materials (BOM)."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BOMComponentBase(BaseModel):
    component_product_id: uuid.UUID
    quantity: Decimal = Field(..., gt=0)
    uom_id: uuid.UUID
    scrap_percentage: Decimal = Decimal("0.00")
    operation_sequence: int | None = None
    position: int = 1
    notes: str | None = None


class BOMComponentCreate(BOMComponentBase):
    pass


class BOMComponentRead(BOMComponentBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    bom_version_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BOMVersionBase(BaseModel):
    version_number: int = 1
    revision_notes: str | None = None
    status: str = "ACTIVE"
    effective_from_date: date | None = None
    effective_to_date: date | None = None


class BOMVersionCreate(BOMVersionBase):
    components: list[BOMComponentCreate] = []


class BOMVersionRead(BOMVersionBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    bom_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    components: list[BOMComponentRead] = []

    model_config = ConfigDict(from_attributes=True)


class BillOfMaterialBase(BaseModel):
    code: str = Field(..., max_length=32)
    name: str = Field(..., max_length=128)
    product_id: uuid.UUID
    routing_id: uuid.UUID | None = None
    quantity: Decimal = Decimal("1.0000")
    uom_id: uuid.UUID
    status: str = "ACTIVE"
    is_default: bool = True
    notes: str | None = None


class BillOfMaterialCreate(BillOfMaterialBase):
    components: list[BOMComponentCreate] = []


class BillOfMaterialUpdate(BaseModel):
    name: str | None = None
    routing_id: uuid.UUID | None = None
    quantity: Decimal | None = None
    status: str | None = None
    is_default: bool | None = None
    notes: str | None = None


class BillOfMaterialRead(BillOfMaterialBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    versions: list[BOMVersionRead] = []

    model_config = ConfigDict(from_attributes=True)
