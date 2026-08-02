import uuid
from datetime import date
from typing import Any

from pydantic import BaseModel


# 1. Branch Schemas
class BranchBase(BaseModel):
    name: str
    slug: str
    code: str | None = None
    is_active: bool | None = True
    parent_branch_id: uuid.UUID | None = None
    manager_id: uuid.UUID | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    country: str | None = None
    state: str | None = None
    city: str | None = None
    postal_code: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    working_hours: dict[str, Any] | None = None
    timezone: str | None = "UTC"


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    code: str | None = None
    is_active: bool | None = None
    parent_branch_id: uuid.UUID | None = None
    manager_id: uuid.UUID | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    country: str | None = None
    state: str | None = None
    city: str | None = None
    postal_code: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    working_hours: dict[str, Any] | None = None
    timezone: str | None = None


class BranchResponse(BranchBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        from_attributes = True


# 2. Department Schemas
class DepartmentBase(BaseModel):
    branch_id: uuid.UUID | None = None
    name: str
    slug: str
    code: str | None = None
    parent_department_id: uuid.UUID | None = None
    manager_id: uuid.UUID | None = None
    budget: float | None = 0.0
    status: str | None = "active"
    settings: dict[str, Any] | None = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    branch_id: uuid.UUID | None = None
    name: str | None = None
    slug: str | None = None
    code: str | None = None
    parent_department_id: uuid.UUID | None = None
    manager_id: uuid.UUID | None = None
    budget: float | None = None
    status: str | None = None
    settings: dict[str, Any] | None = None


class DepartmentResponse(DepartmentBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        from_attributes = True


# 3. Team Schemas
class TeamBase(BaseModel):
    department_id: uuid.UUID
    name: str
    slug: str
    description: str | None = None
    status: str | None = "active"
    parent_team_id: uuid.UUID | None = None
    lead_id: uuid.UUID | None = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    department_id: uuid.UUID | None = None
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    status: str | None = None
    parent_team_id: uuid.UUID | None = None
    lead_id: uuid.UUID | None = None


class TeamResponse(TeamBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        from_attributes = True


# 4. Designation Schemas
class DesignationBase(BaseModel):
    name: str
    slug: str
    code: str | None = None
    job_level: str | None = None
    grade: str | None = None
    title: str
    reporting_level: int | None = 1
    description: str | None = None


class DesignationCreate(DesignationBase):
    pass


class DesignationUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    code: str | None = None
    job_level: str | None = None
    grade: str | None = None
    title: str | None = None
    reporting_level: int | None = None
    description: str | None = None


class DesignationResponse(DesignationBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        from_attributes = True


# 5. Location Schemas
class LocationBase(BaseModel):
    name: str
    type: str | None = "office"
    address_line1: str | None = None
    address_line2: str | None = None
    country: str | None = None
    state: str | None = None
    city: str | None = None
    postal_code: str | None = None
    is_active: bool | None = True


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    country: str | None = None
    state: str | None = None
    city: str | None = None
    postal_code: str | None = None
    is_active: bool | None = None


class LocationResponse(LocationBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        from_attributes = True


# 5b. Business Unit Schemas
class BusinessUnitBase(BaseModel):
    name: str
    slug: str
    code: str | None = None
    description: str | None = None
    manager_id: uuid.UUID | None = None
    status: str | None = "active"


class BusinessUnitCreate(BusinessUnitBase):
    pass


class BusinessUnitUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    code: str | None = None
    description: str | None = None
    manager_id: uuid.UUID | None = None
    status: str | None = None


class BusinessUnitResponse(BusinessUnitBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        from_attributes = True


# 6. Business Calendar Schemas
class BusinessCalendarBase(BaseModel):
    year: int
    name: str
    fiscal_year_start_month: int | None = 1
    is_active: bool | None = True


class BusinessCalendarCreate(BusinessCalendarBase):
    pass


class BusinessCalendarUpdate(BaseModel):
    year: int | None = None
    name: str | None = None
    fiscal_year_start_month: int | None = None
    is_active: bool | None = None


class BusinessCalendarResponse(BusinessCalendarBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        from_attributes = True


# 7. Working Day Schemas
class WorkingDayBase(BaseModel):
    day_of_week: int
    is_working: bool
    start_time: str
    end_time: str


class WorkingDayCreate(WorkingDayBase):
    pass


class WorkingDayResponse(WorkingDayBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    calendar_id: uuid.UUID

    class Config:
        from_attributes = True


# 8. Holiday Schemas
class HolidayBase(BaseModel):
    name: str
    date: date
    type: str
    description: str | None = None


class HolidayCreate(HolidayBase):
    pass


class HolidayResponse(HolidayBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    calendar_id: uuid.UUID

    class Config:
        from_attributes = True


# 9. Document Schemas
class DocumentResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    type: str
    file_path: str
    file_size: int | None = None
    mime_type: str | None = None
    storage_provider: str
    metadata_json: dict[str, Any] | None = None

    class Config:
        from_attributes = True


# 10. Metadata Schemas
class MetadataBase(BaseModel):
    key: str
    value: str
    value_type: str | None = "string"


class MetadataCreate(MetadataBase):
    pass


class MetadataResponse(MetadataBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        from_attributes = True


# 11. Org Settings Schemas
class OrganizationSettingBase(BaseModel):
    fiscal_year_start: str | None = None
    fiscal_year_end: str | None = None
    timezone: str | None = "UTC"
    locale: str | None = "en_US"
    currency: str | None = "USD"
    branding_logo: str | None = None
    branding_primary_color: str | None = "#09090b"
    branding_secondary_color: str | None = "#f4f4f5"
    settings_data: dict[str, Any] | None = None


class OrganizationSettingUpdate(OrganizationSettingBase):
    pass


class OrganizationSettingResponse(OrganizationSettingBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        from_attributes = True


# Reporting Tree Structures
class EmployeeNode(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    designation_title: str | None = None
    job_level: str | None = None
    reporting_level: int | None = None


class ReportingTreeNode(BaseModel):
    user: EmployeeNode
    subordinates: list["ReportingTreeNode"] = []


# Bulk actions
class BulkDeleteRequest(BaseModel):
    ids: list[uuid.UUID]
