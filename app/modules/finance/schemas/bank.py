"""Bank Accounts and Transactions Pydantic Schemas."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BankAccountBase(BaseModel):
    account_name: str = Field(..., min_length=1, max_length=128)
    account_number: str = Field(..., min_length=1, max_length=64)
    bank_name: str = Field(..., min_length=1, max_length=128)
    currency: str = Field("USD", min_length=3, max_length=3)
    gl_account_id: uuid.UUID
    is_active: bool = True


class BankAccountCreate(BankAccountBase):
    pass


class BankAccountResponse(BankAccountBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    current_balance: Decimal
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BankTransactionBase(BaseModel):
    transaction_date: date
    value_date: date
    transaction_type: str = Field(..., max_length=32)  # DEPOSIT, WITHDRAWAL, etc.
    amount: Decimal
    reference: str | None = Field(None, max_length=128)
    description: str | None = Field(None, max_length=255)


class BankTransactionCreate(BankTransactionBase):
    pass


class BankTransactionResponse(BankTransactionBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    bank_account_id: uuid.UUID
    balance_after: Decimal
    is_reconciled: bool
    journal_entry_id: uuid.UUID | None = None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BankAccountListResponse(BaseModel):
    items: list[BankAccountResponse]
    total: int
    page: int
    page_size: int


class BankTransactionListResponse(BaseModel):
    items: list[BankTransactionResponse]
    total: int
    page: int
    page_size: int
