"""Pydantic schemas for User entity management."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreateRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=128)
    password: str = Field(..., min_length=12, max_length=128)
    phone_number: str | None = None
    role_ids: list[uuid.UUID] = Field(default_factory=list)


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=128)
    phone_number: str | None = None
    avatar_url: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    full_name: str
    phone_number: str | None
    avatar_url: str | None
    is_active: bool
    is_verified: bool
    mfa_enabled: bool
    default_organization_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
