"""Learning & Development (LMS), Skills, and Certifications schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------------------------------
# Training Courses & Modules
# --------------------------------------------------------------------------
class CourseModuleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    sequence_order: int = Field(1, ge=1)
    content_type: str = Field("VIDEO", pattern="^(VIDEO|DOCUMENT|QUIZ)$")
    content_url: str | None = None
    duration_minutes: int = Field(30, ge=1)


class CourseModuleResponse(CourseModuleCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    course_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrainingCourseCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=32)
    title: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    category: str = Field("COMPLIANCE", pattern="^(COMPLIANCE|TECHNICAL|LEADERSHIP|ONBOARDING)$")
    duration_hours: float = Field(1.0, ge=0.1)
    provider: str | None = Field("INTERNAL", max_length=128)
    is_mandatory: bool = False
    is_active: bool = True
    modules: list[CourseModuleCreate] = []


class TrainingCourseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    duration_hours: float | None = None
    provider: str | None = None
    is_mandatory: bool | None = None
    is_active: bool | None = None


class TrainingCourseResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    code: str
    title: str
    description: str | None = None
    category: str
    duration_hours: float
    provider: str | None = None
    is_mandatory: bool
    is_active: bool
    version: int
    modules: list[CourseModuleResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Course Enrollments
# --------------------------------------------------------------------------
class CourseEnrollmentCreate(BaseModel):
    employee_id: uuid.UUID
    course_id: uuid.UUID


class CourseEnrollmentProgressUpdate(BaseModel):
    progress_percentage: int = Field(..., ge=0, le=100)
    score: float | None = Field(None, ge=0.0, le=100.0)


class CourseEnrollmentResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    course_id: uuid.UUID
    enrolled_date: date
    status: str
    completion_date: date | None = None
    progress_percentage: int
    score: float | None = None
    certificate_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Employee Skills & Certifications
# --------------------------------------------------------------------------
class EmployeeSkillCreate(BaseModel):
    employee_id: uuid.UUID
    skill_name: str = Field(..., min_length=1, max_length=128)
    proficiency_level: str = Field(
        "INTERMEDIATE", pattern="^(BEGINNER|INTERMEDIATE|ADVANCED|EXPERT)$"
    )
    years_of_experience: float = Field(1.0, ge=0.0, le=50.0)


class EmployeeSkillResponse(EmployeeSkillCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeCertificationCreate(BaseModel):
    employee_id: uuid.UUID
    certification_name: str = Field(..., min_length=1, max_length=255)
    issuing_organization: str = Field(..., min_length=1, max_length=255)
    issue_date: date
    expiry_date: date | None = None
    credential_id: str | None = None
    credential_url: str | None = None


class EmployeeCertificationResponse(EmployeeCertificationCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
