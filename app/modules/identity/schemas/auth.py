"""Pydantic schemas for Authentication, Registration, Sessions, and MFA."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=128)
    tenant_name: str = Field(..., min_length=2, max_length=128)
    tenant_slug: str = Field(..., min_length=2, max_length=64, pattern=r"^[a-z0-9-]+$")
    organization_name: str = Field(..., min_length=2, max_length=128)
    tax_identifier: str = Field(..., min_length=2, max_length=64)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_slug: str | None = None
    mfa_code: str | None = Field(None, min_length=6, max_length=10)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str | None = None
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    roles: list[str]
    permissions: list[str]
    mfa_required: bool = False
    mfa_challenge_token: str | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str | None = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=12, max_length=128)


class MfaSetupResponse(BaseModel):
    secret: str
    otpauth_url: str
    recovery_codes: list[str]


class MfaVerifyRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=10)


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    jti: str
    ip_address: str
    user_agent: str
    device_name: str | None
    is_revoked: bool
    expires_at: datetime
    last_active_at: datetime
    created_at: datetime


class CurrentUserResponse(BaseModel):
    user_id: uuid.UUID
    email: EmailStr
    full_name: str
    tenant_id: uuid.UUID
    organization_id: uuid.UUID | None = None
    roles: list[str]
    permissions: list[str]
    is_active: bool
