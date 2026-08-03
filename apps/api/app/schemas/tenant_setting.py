from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TenantSettingBase(BaseModel):
    currency: str = "USD"
    locale: str = "en_US"
    brand_color_primary: str = "#09090b"
    brand_color_secondary: str = "#f4f4f5"
    business_hours: dict | None = None
    working_days: list | None = None
    fiscal_year_start: int = Field(default=1, ge=1, le=12)


class TenantSettingUpdate(BaseModel):
    currency: str | None = None
    locale: str | None = None
    brand_color_primary: str | None = None
    brand_color_secondary: str | None = None
    business_hours: dict | None = None
    working_days: list | None = None
    fiscal_year_start: int | None = Field(default=None, ge=1, le=12)


class TenantSettingResponse(TenantSettingBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
