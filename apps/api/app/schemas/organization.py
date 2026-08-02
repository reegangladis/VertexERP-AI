import uuid

from pydantic import BaseModel


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    email: str | None = None
    phone: str | None = None
    country: str | None = None
    timezone: str
    status: str
    subscription: str
    logo: str | None = None
    created_by: uuid.UUID | None = None

    class Config:
        from_attributes = True


class OrganizationUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    country: str | None = None
    timezone: str | None = None
    logo: str | None = None


class TenantSettingResponse(BaseModel):
    currency: str
    locale: str
    brand_color_primary: str
    brand_color_secondary: str
    business_hours: dict | None = None
    working_days: list | None = None
    fiscal_year_start: int

    class Config:
        from_attributes = True


class TenantSettingUpdate(BaseModel):
    currency: str | None = None
    locale: str | None = None
    brand_color_primary: str | None = None
    brand_color_secondary: str | None = None
    business_hours: dict | None = None
    working_days: list | None = None
    fiscal_year_start: int | None = None


class SecuritySettingResponse(BaseModel):
    password_min_length: int
    password_require_uppercase: bool
    password_require_lowercase: bool
    password_require_numbers: bool
    password_require_special: bool
    password_expiry_days: int
    session_idle_timeout_minutes: int
    max_concurrent_sessions: int
    account_lockout_threshold: int
    account_lockout_duration_minutes: int

    class Config:
        from_attributes = True


class SecuritySettingUpdate(BaseModel):
    password_min_length: int | None = None
    password_require_uppercase: bool | None = None
    password_require_lowercase: bool | None = None
    password_require_numbers: bool | None = None
    password_require_special: bool | None = None
    password_expiry_days: int | None = None
    session_idle_timeout_minutes: int | None = None
    max_concurrent_sessions: int | None = None
    account_lockout_threshold: int | None = None
    account_lockout_duration_minutes: int | None = None
