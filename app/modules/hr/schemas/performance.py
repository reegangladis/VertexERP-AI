"""Performance Management, Goals/OKRs, and Appraisals schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------------------------------
# Review Periods
# --------------------------------------------------------------------------
class PerformanceReviewPeriodCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=32)
    title: str = Field(..., min_length=1, max_length=128)
    start_date: date
    end_date: date
    self_review_deadline: date | None = None
    manager_review_deadline: date | None = None
    status: str = Field("ACTIVE", pattern="^(PLANNING|ACTIVE|IN_REVIEW|COMPLETED)$")
    is_active: bool = True


class PerformanceReviewPeriodUpdate(BaseModel):
    title: str | None = None
    self_review_deadline: date | None = None
    manager_review_deadline: date | None = None
    status: str | None = None
    is_active: bool | None = None


class PerformanceReviewPeriodResponse(PerformanceReviewPeriodCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Employee Goals / OKRs
# --------------------------------------------------------------------------
class EmployeeGoalCreate(BaseModel):
    employee_id: uuid.UUID
    review_period_id: uuid.UUID | None = None
    title: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    category: str = Field("INDIVIDUAL", pattern="^(INDIVIDUAL|TEAM|COMPANY)$")
    weightage: float = Field(1.0, ge=0.1, le=10.0)
    target_date: date | None = None


class EmployeeGoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    progress_percentage: int | None = Field(None, ge=0, le=100)
    status: str | None = Field(None, pattern="^(NOT_STARTED|IN_PROGRESS|ACHIEVED|MISSED)$")
    self_rating: float | None = Field(None, ge=1.0, le=5.0)
    manager_rating: float | None = Field(None, ge=1.0, le=5.0)


class EmployeeGoalResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    review_period_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    category: str
    weightage: float
    target_date: date | None = None
    progress_percentage: int
    status: str
    self_rating: float | None = None
    manager_rating: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Performance Reviews / Appraisals
# --------------------------------------------------------------------------
class PerformanceReviewCreate(BaseModel):
    employee_id: uuid.UUID
    review_period_id: uuid.UUID
    reviewer_id: uuid.UUID | None = None


class PerformanceReviewSelfSubmit(BaseModel):
    self_score: float = Field(..., ge=0.0, le=100.0)
    strengths: str | None = None
    improvements: str | None = None


class PerformanceReviewManagerSubmit(BaseModel):
    manager_score: float = Field(..., ge=0.0, le=100.0)
    strengths: str | None = None
    improvements: str | None = None
    promotion_recommendation: bool = False
    salary_revision_recommendation: float | None = Field(None, ge=0.0, le=100.0)


class PerformanceReviewFinalize(BaseModel):
    final_score: float = Field(..., ge=0.0, le=100.0)
    final_rating: str = Field(..., pattern="^(OUTSTANDING|EXCEEDS|MEETS|NEEDS_IMPROVEMENT)$")


class PerformanceReviewResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    reviewer_id: uuid.UUID | None = None
    review_period_id: uuid.UUID
    status: str
    self_score: float | None = None
    manager_score: float | None = None
    final_score: float | None = None
    final_rating: str | None = None
    strengths: str | None = None
    improvements: str | None = None
    promotion_recommendation: bool
    salary_revision_recommendation: float | None = None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
