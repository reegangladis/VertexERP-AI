"""CRM Contact Pydantic Schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=64)
    last_name: str = Field(..., min_length=1, max_length=64)
    email: EmailStr
    phone: str | None = Field(None, max_length=32)
    mobile: str | None = Field(None, max_length=32)
    title: str | None = Field(None, max_length=64)
    department: str | None = Field(None, max_length=64)
    customer_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    is_primary: bool = False
    notes: str | None = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=64)
    last_name: str | None = Field(None, min_length=1, max_length=64)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=32)
    mobile: str | None = Field(None, max_length=32)
    title: str | None = Field(None, max_length=64)
    department: str | None = Field(None, max_length=64)
    customer_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    is_primary: bool | None = None
    notes: str | None = None
    custom_fields: dict[str, Any] | None = None
    is_active: bool | None = None


class ContactResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    customer_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    mobile: str | None = None
    title: str | None = None
    department: str | None = None
    is_primary: bool
    notes: str | None = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContactListResponse(BaseModel):
    items: list[ContactResponse]
    total: int
    page: int
    page_size: int
