import uuid
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator


# ──────────────────────────────────────────
# Registration & Login
# ──────────────────────────────────────────

class OrganizationRegister(BaseModel):
    """Full organization + admin user registration payload."""

    # Admin user fields
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=5, max_length=255)
    phone: str | None = Field(None, max_length=30)
    password: str = Field(..., min_length=8)

    # Organization fields
    org_name: str = Field(..., min_length=1, max_length=255, alias="org_name")
    org_slug: str = Field(
        ...,
        min_length=2,
        max_length=80,
        pattern=r"^[a-z0-9-]+$",
    )
    industry: str | None = Field(None, max_length=100)
    company_size: str | None = Field(None, max_length=50)
    country: str | None = Field(None, max_length=100)
    timezone: str | None = Field(None, max_length=60)

    model_config = {"populate_by_name": True}

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        errors = []
        if not any(c.isupper() for c in v):
            errors.append("at least one uppercase letter")
        if not any(c.islower() for c in v):
            errors.append("at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in v):
            errors.append("at least one special character")
        if errors:
            raise ValueError(f"Password must contain {', '.join(errors)}")
        return v


class UserRegister(BaseModel):
    """Legacy/simplified registration schema — keeps backward compatibility."""

    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    username: str = Field(..., min_length=3)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8)
    org_name: str = Field(..., min_length=1)
    org_slug: str = Field(..., min_length=2)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        errors = []
        if not any(c.isupper() for c in v):
            errors.append("at least one uppercase letter")
        if not any(c.islower() for c in v):
            errors.append("at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in v):
            errors.append("at least one special character")
        if errors:
            raise ValueError(f"Password must contain {', '.join(errors)}")
        return v


class UserLogin(BaseModel):
    email: str | None = None
    username: str | None = None
    identifier: str | None = None
    password: str
    remember_me: bool = False


# ──────────────────────────────────────────
# Token Schemas
# ──────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    session_id: str | None = None


class RefreshInput(BaseModel):
    refresh_token: str


# ──────────────────────────────────────────
# Password Management
# ──────────────────────────────────────────

class ForgotPasswordInput(BaseModel):
    email: str


class ResetPasswordInput(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        errors = []
        if not any(c.isupper() for c in v):
            errors.append("at least one uppercase letter")
        if not any(c.islower() for c in v):
            errors.append("at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in v):
            errors.append("at least one special character")
        if errors:
            raise ValueError(f"Password must contain {', '.join(errors)}")
        return v


class ChangePasswordInput(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        errors = []
        if not any(c.isupper() for c in v):
            errors.append("at least one uppercase letter")
        if not any(c.islower() for c in v):
            errors.append("at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in v):
            errors.append("at least one special character")
        if errors:
            raise ValueError(f"Password must contain {', '.join(errors)}")
        return v


class EmailVerificationInput(BaseModel):
    token: str


# ──────────────────────────────────────────
# Profile Update
# ──────────────────────────────────────────

class UserUpdate(BaseModel):
    """Payload for updating the current user's profile fields."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    phone: str | None = Field(None, max_length=30)
    avatar: str | None = Field(None, max_length=1024)
    timezone: str | None = Field(None, max_length=60)
    language: str | None = Field(None, max_length=10)


# ──────────────────────────────────────────
# Response Schemas
# ──────────────────────────────────────────

class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    username: str
    email: str
    phone: str | None = None
    avatar: str | None = None
    status: str
    email_verified: bool
    phone_verified: bool
    last_login: datetime | None = None
    timezone: str
    language: str
    mfa_enabled: bool
    organization_id: uuid.UUID | None = None
    roles: list[RoleResponse] = []

    model_config = {"from_attributes": True}


class SessionResponse(BaseModel):
    id: uuid.UUID
    ip_address: str
    user_agent: str
    device_info: str | None = None
    is_active: bool
    expires_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginHistoryResponse(BaseModel):
    id: uuid.UUID
    email: str
    ip_address: str
    user_agent: str
    browser: str | None = None
    os: str | None = None
    status: str
    failure_reason: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    action: str
    ip_address: str
    user_agent: str
    details: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ForgotPasswordResponse(BaseModel):
    """Dev-mode response that includes the reset token directly."""

    message: str
    reset_token: str | None = None   # Only populated in development environment


class VerifyEmailResponse(BaseModel):
    """Dev-mode response that includes the verification token."""

    message: str
    verification_token: str | None = None  # Only populated in development environment
