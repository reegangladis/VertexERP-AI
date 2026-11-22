"""Payment and Payment Allocation Pydantic Schemas."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PaymentAllocationCreate(BaseModel):
    invoice_id: uuid.UUID | None = None
    bill_id: uuid.UUID | None = None
    allocated_amount: Decimal = Field(..., gt=0)


class PaymentAllocationResponse(PaymentAllocationCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    payment_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentBase(BaseModel):
    payment_type: str = Field(..., max_length=32)  # RECEIPT, DISBURSEMENT
    partner_type: str = Field(..., max_length=32)  # CUSTOMER, VENDOR
    partner_id: uuid.UUID
    payment_date: date
    payment_method: str = Field("BANK", max_length=32)
    bank_account_id: uuid.UUID | None = None
    currency: str = Field("USD", min_length=3, max_length=3)
    amount: Decimal = Field(..., gt=0)
    reference: str | None = Field(None, max_length=128)
    notes: str | None = None


class PaymentCreate(PaymentBase):
    payment_number: str | None = None
    allocations: list[PaymentAllocationCreate] = Field(default_factory=list)


class PaymentResponse(PaymentBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    payment_number: str
    allocated_amount: Decimal
    unallocated_amount: Decimal
    status: str
    posted_journal_entry_id: uuid.UUID | None = None
    version: int
    allocations: list[PaymentAllocationResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentListResponse(BaseModel):
    items: list[PaymentResponse]
    total: int
    page: int
    page_size: int
