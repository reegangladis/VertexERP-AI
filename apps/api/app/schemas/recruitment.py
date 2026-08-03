import uuid
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Recruitment Job Schemas ---
class RecruitmentJobCreate(BaseModel):
    organization_id: uuid.UUID
    department_id: uuid.UUID | None = None
    designation_id: uuid.UUID | None = None
    job_title: str = Field(..., max_length=255)
    job_code: str = Field(..., max_length=50)
    employment_type: str = "Full-Time"
    location: str | None = None
    experience_required: str | None = None
    salary_min: float = 0.0
    salary_max: float = 0.0
    vacancies: int = Field(1, ge=1)
    description: str | None = None
    requirements: str | None = None
    status: str = "Open"
    opening_date: date | None = None
    closing_date: date | None = None


class RecruitmentJobUpdate(BaseModel):
    job_title: str | None = None
    department_id: uuid.UUID | None = None
    designation_id: uuid.UUID | None = None
    employment_type: str | None = None
    location: str | None = None
    experience_required: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    vacancies: int | None = None
    description: str | None = None
    requirements: str | None = None
    status: str | None = None
    opening_date: date | None = None
    closing_date: date | None = None


class RecruitmentJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    department_id: uuid.UUID | None = None
    designation_id: uuid.UUID | None = None
    job_title: str
    job_code: str
    employment_type: str
    location: str | None = None
    experience_required: str | None = None
    salary_min: float
    salary_max: float
    vacancies: int
    description: str | None = None
    requirements: str | None = None
    status: str
    opening_date: date | None = None
    closing_date: date | None = None
    created_at: datetime
    updated_at: datetime


# --- Candidate Schemas ---
class CandidateCreate(BaseModel):
    organization_id: uuid.UUID
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    phone: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    resume_url: str | None = None
    current_company: str | None = None
    current_designation: str | None = None
    experience_years: float = 0.0
    expected_salary: float = 0.0
    current_salary: float = 0.0
    notice_period: str | None = None
    status: str = "New"


class CandidateUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    resume_url: str | None = None
    current_company: str | None = None
    current_designation: str | None = None
    experience_years: float | None = None
    expected_salary: float | None = None
    current_salary: float | None = None
    notice_period: str | None = None
    status: str | None = None


class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    resume_url: str | None = None
    current_company: str | None = None
    current_designation: str | None = None
    experience_years: float
    expected_salary: float
    current_salary: float
    notice_period: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


# --- Application & Pipeline Schemas ---
class ApplicationCreate(BaseModel):
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    applied_date: date | None = None
    application_source: str = "Website"
    screening_notes: str | None = None


class ApplicationMoveStage(BaseModel):
    new_stage: Literal["Applied", "Screening", "Interview", "Offer", "Hired", "Rejected", "Withdrawn"]
    changed_by: uuid.UUID | None = None
    remarks: str | None = None


class RecruitmentPipelineLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    previous_stage: str
    new_stage: str
    changed_by: uuid.UUID | None = None
    changed_at: datetime
    remarks: str | None = None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    applied_date: date
    application_source: str
    status: str
    resume_score: float
    screening_notes: str | None = None
    pipeline_logs: list[RecruitmentPipelineLogResponse] = []
    created_at: datetime
    updated_at: datetime


# --- Interview Schemas ---
class InterviewRoundCreate(BaseModel):
    application_id: uuid.UUID
    round_name: str = Field(..., max_length=100)
    round_number: int = 1
    interviewer_id: uuid.UUID | None = None
    scheduled_at: datetime
    meeting_link: str | None = None
    status: str = "Scheduled"


class InterviewRoundUpdate(BaseModel):
    round_name: str | None = None
    interviewer_id: uuid.UUID | None = None
    scheduled_at: datetime | None = None
    meeting_link: str | None = None
    status: str | None = None


class InterviewFeedbackCreate(BaseModel):
    interview_round_id: uuid.UUID
    technical_score: float = Field(0.0, ge=0.0, le=5.0)
    communication_score: float = Field(0.0, ge=0.0, le=5.0)
    problem_solving_score: float = Field(0.0, ge=0.0, le=5.0)
    culture_fit_score: float = Field(0.0, ge=0.0, le=5.0)
    recommendation: Literal["Hire", "Strong Hire", "No Hire", "Hold"] = "Hire"
    comments: str | None = None


class InterviewFeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    interview_round_id: uuid.UUID
    technical_score: float
    communication_score: float
    problem_solving_score: float
    culture_fit_score: float
    overall_score: float
    recommendation: str
    comments: str | None = None
    submitted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class InterviewRoundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    round_name: str
    round_number: int
    interviewer_id: uuid.UUID | None = None
    scheduled_at: datetime
    meeting_link: str | None = None
    status: str
    feedback: list[InterviewFeedbackResponse] = []
    created_at: datetime
    updated_at: datetime


# --- Job Offer Schemas ---
class JobOfferCreate(BaseModel):
    application_id: uuid.UUID
    offered_salary: float
    joining_bonus: float = 0.0
    joining_date: date
    offer_letter_url: str | None = None


class JobOfferUpdate(BaseModel):
    offered_salary: float | None = None
    joining_bonus: float | None = None
    joining_date: date | None = None
    offer_letter_url: str | None = None
    status: Literal["Draft", "Sent", "Approved", "Accepted", "Rejected", "Expired"] | None = None


class JobOfferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    offered_salary: float
    joining_bonus: float
    joining_date: date
    offer_letter_url: str | None = None
    status: str
    offered_at: datetime | None = None
    accepted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


# --- Candidate Document Schemas ---
class CandidateDocumentCreate(BaseModel):
    candidate_id: uuid.UUID
    document_name: str = Field(..., max_length=255)
    document_type: str = Field(..., max_length=100)
    file_url: str = Field(..., max_length=500)


class CandidateDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    candidate_id: uuid.UUID
    document_name: str
    document_type: str
    file_url: str
    verified: bool
    created_at: datetime
    updated_at: datetime


# --- Onboarding Task Schemas ---
class OnboardingTaskCreate(BaseModel):
    offer_id: uuid.UUID
    task_name: str = Field(..., max_length=255)
    assigned_to: uuid.UUID | None = None
    due_date: date | None = None


class OnboardingTaskUpdate(BaseModel):
    task_name: str | None = None
    assigned_to: uuid.UUID | None = None
    due_date: date | None = None
    status: Literal["Pending", "In Progress", "Completed"] | None = None


class OnboardingTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    offer_id: uuid.UUID
    task_name: str
    assigned_to: uuid.UUID | None = None
    status: str
    due_date: date | None = None
    created_at: datetime
    updated_at: datetime


# --- Agency & Dashboard Schemas ---
class RecruitmentAgencyCreate(BaseModel):
    organization_id: uuid.UUID
    agency_name: str = Field(..., max_length=255)
    contact_person: str = Field(..., max_length=100)
    email: EmailStr
    phone: str | None = None
    website: str | None = None


class RecruitmentAgencyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    agency_name: str
    contact_person: str
    email: str
    phone: str | None = None
    website: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class RecruitmentDashboardSummary(BaseModel):
    open_positions: int
    candidates_applied: int
    interviews_today: int
    offers_sent: int
    offers_accepted: int
    hiring_pipeline: dict[str, int]
    time_to_hire: float


# Backward compatibility aliases
JobRequisitionCreate = RecruitmentJobCreate
JobRequisitionResponse = RecruitmentJobResponse
ApplicationStageUpdate = ApplicationMoveStage
JobOfferAction = JobOfferUpdate
