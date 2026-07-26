import uuid
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class UserRegister(BaseModel):
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
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for char in v):
            raise ValueError("Password must contain at least one special character")
        return v

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    session_id: str | None = None

class RefreshInput(BaseModel):
    refresh_token: str

class ForgotPasswordInput(BaseModel):
    email: str

class ResetPasswordInput(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    username: str
    email: str
    phone: str | None = None
    status: str
    email_verified: bool
    phone_verified: bool
    last_login: datetime | None = None
    timezone: str
    language: str
    mfa_enabled: bool
    organization_id: uuid.UUID | None = None

    class Config:
        from_attributes = True

class SessionResponse(BaseModel):
    id: uuid.UUID
    ip_address: str
    user_agent: str
    device_info: str | None = None
    is_active: bool
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

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

    class Config:
        from_attributes = True

class EmailVerificationInput(BaseModel):
    token: str
