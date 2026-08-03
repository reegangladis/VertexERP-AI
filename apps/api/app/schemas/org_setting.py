from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationSettingBase(BaseModel):
    company_name: str | None = None
    website: str | None = None
    gst_number: str | None = None
    pan_number: str | None = None
    default_language: str = "en"
    default_currency: str = "USD"
    timezone: str = "UTC"
    date_format: str = "YYYY-MM-DD"
    time_format: str = "24h"
    week_start: str = "Monday"
    logo: str | None = None
    favicon: str | None = None
    theme: str = "light"


class OrganizationSettingUpdate(BaseModel):
    company_name: str | None = None
    website: str | None = None
    gst_number: str | None = None
    pan_number: str | None = None
    default_language: str | None = None
    default_currency: str | None = None
    timezone: str | None = None
    date_format: str | None = None
    time_format: str | None = None
    week_start: str | None = None
    logo: str | None = None
    favicon: str | None = None
    theme: str | None = None


class OrganizationSettingResponse(OrganizationSettingBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
