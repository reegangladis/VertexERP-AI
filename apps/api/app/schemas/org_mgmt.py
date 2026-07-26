import uuid
from datetime import date
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

# 1. Branch Schemas
class BranchBase(BaseModel):
    name: str
    slug: str
    code: Optional[str] = None
    is_active: Optional[bool] = True
    parent_branch_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    working_hours: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = "UTC"

class BranchCreate(BranchBase):
    pass

class BranchUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    code: Optional[str] = None
    is_active: Optional[bool] = None
    parent_branch_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    working_hours: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None

class BranchResponse(BranchBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        from_attributes = True


# 2. Department Schemas
class DepartmentBase(BaseModel):
    branch_id: Optional[uuid.UUID] = None
    name: str
    slug: str
    code: Optional[str] = None
    parent_department_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    budget: Optional[float] = 0.0
    status: Optional[str] = "active"
    settings: Optional[Dict[str, Any]] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    branch_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    code: Optional[str] = None
    parent_department_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    budget: Optional[float] = None
    status: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

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
    description: Optional[str] = None
    status: Optional[str] = "active"
    parent_team_id: Optional[uuid.UUID] = None
    lead_id: Optional[uuid.UUID] = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    department_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    parent_team_id: Optional[uuid.UUID] = None
    lead_id: Optional[uuid.UUID] = None

class TeamResponse(TeamBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        from_attributes = True


# 4. Designation Schemas
class DesignationBase(BaseModel):
    name: str
    slug: str
    code: Optional[str] = None
    job_level: Optional[str] = None
    grade: Optional[str] = None
    title: str
    reporting_level: Optional[int] = 1
    description: Optional[str] = None

class DesignationCreate(DesignationBase):
    pass

class DesignationUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    code: Optional[str] = None
    job_level: Optional[str] = None
    grade: Optional[str] = None
    title: Optional[str] = None
    reporting_level: Optional[int] = None
    description: Optional[str] = None

class DesignationResponse(DesignationBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        from_attributes = True


# 5. Location Schemas
class LocationBase(BaseModel):
    name: str
    type: Optional[str] = "office"
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    is_active: Optional[bool] = True

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    is_active: Optional[bool] = None

class LocationResponse(LocationBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        from_attributes = True


# 6. Business Calendar Schemas
class BusinessCalendarBase(BaseModel):
    year: int
    name: str
    fiscal_year_start_month: Optional[int] = 1
    is_active: Optional[bool] = True

class BusinessCalendarCreate(BusinessCalendarBase):
    pass

class BusinessCalendarUpdate(BaseModel):
    year: Optional[int] = None
    name: Optional[str] = None
    fiscal_year_start_month: Optional[int] = None
    is_active: Optional[bool] = None

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
    description: Optional[str] = None

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
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    storage_provider: str
    metadata_json: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# 10. Metadata Schemas
class MetadataBase(BaseModel):
    key: str
    value: str
    value_type: Optional[str] = "string"

class MetadataCreate(MetadataBase):
    pass

class MetadataResponse(MetadataBase):
    id: uuid.UUID
    organization_id: uuid.UUID

    class Config:
        from_attributes = True


# 11. Org Settings Schemas
class OrganizationSettingBase(BaseModel):
    fiscal_year_start: Optional[str] = None
    fiscal_year_end: Optional[str] = None
    timezone: Optional[str] = "UTC"
    locale: Optional[str] = "en_US"
    currency: Optional[str] = "USD"
    branding_logo: Optional[str] = None
    branding_primary_color: Optional[str] = "#09090b"
    branding_secondary_color: Optional[str] = "#f4f4f5"
    settings_data: Optional[Dict[str, Any]] = None

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
    designation_title: Optional[str] = None
    job_level: Optional[str] = None
    reporting_level: Optional[int] = None

class ReportingTreeNode(BaseModel):
    user: EmployeeNode
    subordinates: List["ReportingTreeNode"] = []

# Bulk actions
class BulkDeleteRequest(BaseModel):
    ids: List[uuid.UUID]
