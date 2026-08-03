from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EmployeeProfileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    employee_id: UUID | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None
    biography: str | None = None
    languages: str | None = None
    hobbies: str | None = None
    skills_summary: str | None = None


class EmployeeProfileUpdate(BaseModel):
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None
    biography: str | None = None
    languages: str | None = None
    hobbies: str | None = None
    skills_summary: str | None = None


class EmployeeDocumentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    employee_id: UUID | None = None
    document_type: str
    document_name: str
    document_number: str | None = None
    file_url: str
    issued_date: datetime | None = None
    expiry_date: datetime | None = None
    verified: bool = False


class EmployeeNoteSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    employee_id: UUID | None = None
    title: str
    note: str
    visibility: str = "public"
    created_by: UUID | None = None
    created_at: datetime | None = None


class EmergencyContactSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    employee_id: UUID | None = None
    contact_name: str
    relationship: str
    phone: str
    email: str | None = None
    address: str | None = None
    priority: int = 1


class EmployeeSkillSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    employee_id: UUID | None = None
    skill_name: str
    category: str | None = None
    proficiency: str = "intermediate"
    years_of_experience: float | None = None
    verified: bool = False


class CertificationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    employee_id: UUID | None = None
    certification_name: str
    issuer: str
    issue_date: datetime | None = None
    expiry_date: datetime | None = None
    credential_id: str | None = None
    credential_url: str | None = None


class EmploymentHistorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    employee_id: UUID | None = None
    company: str
    designation: str | None = None
    department: str | None = None
    joining_date: datetime | None = None
    leaving_date: datetime | None = None
    reason: str | None = None


class EmployeeAssetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    employee_id: UUID | None = None
    asset_name: str
    asset_code: str
    asset_type: str | None = None
    assigned_date: datetime | None = None
    returned_date: datetime | None = None
    status: str = "assigned"


class EmployeeTimelineSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    employee_id: UUID | None = None
    event_type: str
    title: str
    description: str | None = None
    event_date: datetime | None = None
    created_by: UUID | None = None


class EmployeeBase(BaseModel):
    employee_code: str
    first_name: str
    middle_name: str | None = None
    last_name: str
    gender: str | None = None
    date_of_birth: datetime | None = None
    marital_status: str | None = None
    blood_group: str | None = None
    joining_date: datetime | None = None
    confirmation_date: datetime | None = None
    employment_type: str = "full_time"
    employment_status: str = "active"
    official_email: str
    personal_email: str | None = None
    official_phone: str | None = None
    personal_phone: str | None = None
    nationality: str | None = None
    photo: str | None = None
    manager_uuid: UUID | None = None
    status: str = "active"


class EmployeeCreate(EmployeeBase):
    organization_id: UUID
    department_id: UUID | None = None
    designation_id: UUID | None = None
    business_unit_id: UUID | None = None
    branch_id: UUID | None = None
    user_id: UUID | None = None
    profile: EmployeeProfileSchema | None = None


class EmployeeUpdate(BaseModel):
    employee_code: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    gender: str | None = None
    date_of_birth: datetime | None = None
    marital_status: str | None = None
    blood_group: str | None = None
    joining_date: datetime | None = None
    confirmation_date: datetime | None = None
    employment_type: str | None = None
    employment_status: str | None = None
    official_email: str | None = None
    personal_email: str | None = None
    official_phone: str | None = None
    personal_phone: str | None = None
    nationality: str | None = None
    photo: str | None = None
    department_id: UUID | None = None
    designation_id: UUID | None = None
    business_unit_id: UUID | None = None
    branch_id: UUID | None = None
    user_id: UUID | None = None
    manager_uuid: UUID | None = None
    status: str | None = None


class EmployeeResponse(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    department_id: UUID | None = None
    designation_id: UUID | None = None
    business_unit_id: UUID | None = None
    branch_id: UUID | None = None
    user_id: UUID | None = None
    profile: EmployeeProfileSchema | None = None
    documents: list[EmployeeDocumentSchema] = []
    notes: list[EmployeeNoteSchema] = []
    emergency_contacts: list[EmergencyContactSchema] = []
    skills: list[EmployeeSkillSchema] = []
    certifications: list[CertificationSchema] = []
    history: list[EmploymentHistorySchema] = []
    assets: list[EmployeeAssetSchema] = []
    timeline: list[EmployeeTimelineSchema] = []
    created_at: datetime
    updated_at: datetime
