from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.role import RoleResponse


class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., min_length=3, max_length=255)
    phone: str | None = None
    avatar: str | None = None
    timezone: str = "UTC"
    language: str = "en"


class UserCreate(UserBase):
    organization_id: UUID | None = None
    password: str = Field(..., min_length=8)
    role_ids: list[UUID] = []


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    avatar: str | None = None
    timezone: str | None = None
    language: str | None = None
    status: str | None = None
    role_ids: list[UUID] | None = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID | None = None
    status: str
    email_verified: bool = False
    phone_verified: bool = False
    mfa_enabled: bool = False
    last_login: datetime | None = None
    failed_login_attempts: int = 0
    locked_until: datetime | None = None
    created_at: datetime
    updated_at: datetime


class UserWithRolesResponse(UserResponse):
    roles: list[RoleResponse] = []
