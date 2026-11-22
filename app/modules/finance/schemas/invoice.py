"""Sales Invoices (AR) Pydantic Schemas."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class InvoiceLineBase(BaseModel):
    product_id: uuid.UUID | None = None
    description: str = Field(..., min_length=1, max_length=255)
    account_id: uuid.UUID
    quantity: Decimal = Field(Decimal("1.0000"), gt=0)
    unit_price: Decimal = Field(Decimal("0.0000"), ge=0)
    tax_rate: Decimal = Field(Decimal("0.0000"), ge=0)


class InvoiceLineCreate(InvoiceLineBase):
    pass


class InvoiceLineResponse(InvoiceLineBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    invoice_id: uuid.UUID
    tax_amount: Decimal
    line_total: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceBase(BaseModel):
    customer_id: uuid.UUID
    issue_date: date
    due_date: date
    currency: str = Field("USD", min_length=3, max_length=3)
    exchange_rate: Decimal = Field(Decimal("1.000000"), gt=0)
    ar_account_id: uuid.UUID | None = None
    notes: str | None = None


class InvoiceCreate(InvoiceBase):
    invoice_number: str | None = None
    lines: list[InvoiceLineCreate] = Field(..., min_length=1)


class InvoiceResponse(InvoiceBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    invoice_number: str
    subtotal_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    amount_due: Decimal
    status: str
    posted_journal_entry_id: uuid.UUID | None = None
    version: int
    lines: list[InvoiceLineResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceListResponse(BaseModel):
    items: list[InvoiceResponse]
    total: int
    page: int
    page_size: int
