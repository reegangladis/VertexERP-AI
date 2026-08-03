from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SecuritySettingBase(BaseModel):
    password_policy: dict | None = None
    mfa_required: bool = False
    session_timeout: int = 30
    login_attempt_limit: int = 5
    lockout_duration: int = 15
    allowed_domains: list | None = None
    ip_whitelist: list | None = None


class SecuritySettingUpdate(BaseModel):
    password_policy: dict | None = None
    mfa_required: bool | None = None
    session_timeout: int | None = None
    login_attempt_limit: int | None = None
    lockout_duration: int | None = None
    allowed_domains: list | None = None
    ip_whitelist: list | None = None


class SecuritySettingResponse(SecuritySettingBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
