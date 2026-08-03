from pydantic import BaseModel, Field


class MfaSecretResponse(BaseModel):
    totp_secret: str
    qr_code_url: str
    backup_codes: list[str]


class MfaVerifyRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)


class MfaToggleRequest(BaseModel):
    enabled: bool
