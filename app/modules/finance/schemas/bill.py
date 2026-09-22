"""Vendor Bills (AP) Pydantic Schemas."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BillLineBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=255)
    expense_account_id: uuid.UUID
    quantity: Decimal = Field(Decimal("1.0000"), gt=0)
    unit_price: Decimal = Field(Decimal("0.0000"), ge=0)
    tax_rate: Decimal = Field(Decimal("0.0000"), ge=0)


class BillLineCreate(BillLineBase):
    pass


class BillLineResponse(BillLineBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    bill_id: uuid.UUID
    tax_amount: Decimal
    line_total: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BillBase(BaseModel):
    vendor_id: uuid.UUID
    vendor_invoice_ref: str | None = Field(None, max_length=128)
    bill_date: date
    due_date: date
    currency: str = Field("USD", min_length=3, max_length=3)
    exchange_rate: Decimal = Field(Decimal("1.000000"), gt=0)
    ap_account_id: uuid.UUID | None = None
    notes: str | None = None


class BillCreate(BillBase):
    bill_number: str | None = None
    lines: list[BillLineCreate] = Field(..., min_length=1)


class BillResponse(BillBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    bill_number: str
    subtotal_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    amount_due: Decimal
    status: str
    posted_journal_entry_id: uuid.UUID | None = None
    version: int
    lines: list[BillLineResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BillListResponse(BaseModel):
    items: list[BillResponse]
    total: int
    page: int
    page_size: int
