"""Chart of Accounts Pydantic Schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AccountBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=128)
    account_type: str = Field(..., max_length=32)  # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    account_category: str = Field("CURRENT_ASSET", max_length=64)
    parent_account_id: uuid.UUID | None = None
    currency: str = Field("USD", min_length=3, max_length=3)
    is_reconciled: bool = False
    is_active: bool = True


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    account_category: str | None = None
    parent_account_id: uuid.UUID | None = None
    currency: str | None = None
    is_reconciled: bool | None = None
    is_active: bool | None = None


class AccountResponse(AccountBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    is_deleted: bool
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountListResponse(BaseModel):
    items: list[AccountResponse]
    total: int
    page: int
    page_size: int
