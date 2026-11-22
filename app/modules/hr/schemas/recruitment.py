"""Recruitment, Job Requisitions, Applicants, Interviews, and Offers schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------------------------------
# Job Requisitions
# --------------------------------------------------------------------------
class JobRequisitionCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    department_id: uuid.UUID | None = None
    designation_id: uuid.UUID | None = None
    headcount: int = Field(1, ge=1)
    employment_type: str = Field("FULL_TIME", pattern="^(FULL_TIME|PART_TIME|CONTRACT|INTERN)$")
    experience_level: str = Field("MID", pattern="^(ENTRY|MID|SENIOR|LEAD|EXECUTIVE)$")
    salary_min: float = Field(0.0, ge=0.0)
    salary_max: float = Field(0.0, ge=0.0)
    target_hire_date: date | None = None
    description: str | None = None


class JobRequisitionUpdate(BaseModel):
    title: str | None = None
    headcount: int | None = None
    employment_type: str | None = None
    experience_level: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    status: str | None = None
    target_hire_date: date | None = None
    description: str | None = None


class JobRequisitionResponse(JobRequisitionCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    requisition_number: str
    status: str
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Job Applicants
# --------------------------------------------------------------------------
class JobApplicantCreate(BaseModel):
    requisition_id: uuid.UUID
    first_name: str = Field(..., min_length=1, max_length=64)
    last_name: str = Field(..., min_length=1, max_length=64)
    email: str = Field(..., min_length=3, max_length=255)
    phone: str | None = None
    resume_url: str | None = None
    source: str | None = None


class JobApplicantStageUpdate(BaseModel):
    current_stage: str = Field(..., pattern="^(APPLIED|SCREENING|INTERVIEW|OFFER|HIRED|REJECTED)$")
    rating: int = Field(0, ge=0, le=5)


class JobApplicantResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    requisition_id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    resume_url: str | None = None
    current_stage: str
    rating: int
    source: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Interview Schedules
# --------------------------------------------------------------------------
class InterviewScheduleCreate(BaseModel):
    applicant_id: uuid.UUID
    interviewer_id: uuid.UUID | None = None
    interview_type: str = Field("TECHNICAL", pattern="^(PHONE|TECHNICAL|MANAGERIAL|HR)$")
    scheduled_at: datetime
    duration_minutes: int = Field(45, ge=15, le=240)
    meeting_link: str | None = None


class InterviewScheduleResponse(InterviewScheduleCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Interview Feedback
# --------------------------------------------------------------------------
class InterviewFeedbackCreate(BaseModel):
    interview_id: uuid.UUID
    rating: int = Field(3, ge=1, le=5)
    score: float = Field(0.0, ge=0.0, le=100.0)
    strengths: str | None = None
    weaknesses: str | None = None
    recommendation: str = Field("HIRE", pattern="^(STRONG_HIRE|HIRE|HOLD|REJECT)$")
    notes: str | None = None


class InterviewFeedbackResponse(InterviewFeedbackCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    interviewer_id: uuid.UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Job Offers
# --------------------------------------------------------------------------
class JobOfferCreate(BaseModel):
    applicant_id: uuid.UUID
    offered_designation_id: uuid.UUID | None = None
    offered_salary: float = Field(..., gt=0.0)
    currency: str = Field("USD", min_length=3, max_length=3)
    joining_date: date
    expiry_date: date | None = None


class JobOfferStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(DRAFT|SENT|ACCEPTED|DECLINED|WITHDRAWN)$")


class JobOfferResponse(JobOfferCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
