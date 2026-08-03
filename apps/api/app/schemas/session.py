from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    device_name: str | None = None
    device_type: str | None = None
    browser: str | None = None
    operating_system: str | None = None
    ip_address: str
    location: str | None = None
    expires_at: datetime
    last_activity: datetime
    revoked: bool = False


class LoginHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None = None
    login_time: datetime
    logout_time: datetime | None = None
    ip_address: str
    device: str | None = None
    browser: str | None = None
    location: str | None = None
    status: str = "success"


class TrustedDeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    device_name: str | None = None
    device_identifier: str
    last_used: datetime
    trusted_until: datetime
