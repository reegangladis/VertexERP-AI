"""Journal Entry, Journal Line, and General Ledger Pydantic Schemas."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class JournalLineBase(BaseModel):
    account_id: uuid.UUID
    debit: Decimal = Field(Decimal("0.0000"), ge=0)
    credit: Decimal = Field(Decimal("0.0000"), ge=0)
    currency: str = Field("USD", min_length=3, max_length=3)
    partner_type: str | None = None  # CUSTOMER, VENDOR, EMPLOYEE, NONE
    partner_id: uuid.UUID | None = None
    description: str | None = Field(None, max_length=255)
    cost_center_id: uuid.UUID | None = None


class JournalLineCreate(JournalLineBase):
    line_number: int | None = None


class JournalLineResponse(JournalLineBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    journal_entry_id: uuid.UUID
    line_number: int
    currency_debit: Decimal
    currency_credit: Decimal
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JournalEntryBase(BaseModel):
    entry_date: date
    posting_date: date
    fiscal_period_id: uuid.UUID | None = None
    entry_type: str = Field("STANDARD", max_length=32)
    reference_type: str | None = None
    reference_id: str | None = None
    currency: str = Field("USD", min_length=3, max_length=3)
    exchange_rate: Decimal = Field(Decimal("1.000000"), gt=0)
    notes: str | None = None


class JournalEntryCreate(JournalEntryBase):
    entry_number: str | None = None
    lines: list[JournalLineCreate] = Field(..., min_length=2)


class JournalEntryResponse(JournalEntryBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    entry_number: str
    status: str
    total_debit: Decimal
    total_credit: Decimal
    posted_by_id: uuid.UUID | None = None
    posted_at: datetime | None = None
    reversed_by_entry_id: uuid.UUID | None = None
    version: int
    lines: list[JournalLineResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JournalEntryListResponse(BaseModel):
    items: list[JournalEntryResponse]
    total: int
    page: int
    page_size: int


class GeneralLedgerResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    account_id: uuid.UUID
    journal_entry_id: uuid.UUID
    journal_line_id: uuid.UUID
    posting_date: date
    fiscal_period_id: uuid.UUID | None = None
    debit: Decimal
    credit: Decimal
    balance_after: Decimal
    currency: str
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GeneralLedgerListResponse(BaseModel):
    items: list[GeneralLedgerResponse]
    total: int
    page: int
    page_size: int
