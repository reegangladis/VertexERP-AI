import uuid
from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


# --- Goal & Key Result Schemas ---
class KeyResultBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    target_value: float = Field(default=100.0, ge=0)
    current_value: float = Field(default=0.0, ge=0)
    measurement_unit: str = Field(default="Percentage", max_length=50)
    progress: float = Field(default=0.0, ge=0, le=100)
    status: str = Field(default="Not Started", max_length=50)


class KeyResultCreate(KeyResultBase):
    goal_id: uuid.UUID | None = None


class KeyResultUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    target_value: float | None = Field(None, ge=0)
    current_value: float | None = Field(None, ge=0)
    measurement_unit: str | None = Field(None, max_length=50)
    progress: float | None = Field(None, ge=0, le=100)
    status: str | None = Field(None, max_length=50)


class KeyResultResponse(KeyResultBase):
    id: uuid.UUID
    goal_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GoalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    goal_type: str = Field(default="OKR", max_length=50)
    priority: str = Field(default="Medium", max_length=50)
    weightage: float = Field(default=100.0, ge=0)
    start_date: date
    end_date: date
    status: str = Field(default="Draft", max_length=50)
    progress: float = Field(default=0.0, ge=0, le=100)


class GoalCreate(GoalBase):
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    key_results: list[KeyResultCreate] = Field(default_factory=list)


class GoalUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    goal_type: str | None = Field(None, max_length=50)
    priority: str | None = Field(None, max_length=50)
    weightage: float | None = Field(None, ge=0)
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = Field(None, max_length=50)
    progress: float | None = Field(None, ge=0, le=100)


class GoalResponse(GoalBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    key_results: list[KeyResultResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Performance Review & Feedback Schemas ---
class PerformanceReviewCycleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    review_type: str = Field(default="Annual", max_length=50)
    start_date: date
    end_date: date
    status: str = Field(default="Draft", max_length=50)


class PerformanceReviewCycleCreate(PerformanceReviewCycleBase):
    organization_id: uuid.UUID


class PerformanceReviewCycleUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    review_type: str | None = Field(None, max_length=50)
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = Field(None, max_length=50)


class PerformanceReviewCycleResponse(PerformanceReviewCycleBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PerformanceFeedbackBase(BaseModel):
    feedback_type: str = Field(..., max_length=50)  # Self, Manager, Peer, 360
    comments: str | None = Field(None, max_length=4000)
    rating: float | None = Field(None, ge=0, le=5)


class PerformanceFeedbackCreate(PerformanceFeedbackBase):
    review_id: uuid.UUID
    submitted_by: uuid.UUID


class PerformanceFeedbackUpdate(BaseModel):
    comments: str | None = Field(None, max_length=4000)
    rating: float | None = Field(None, ge=0, le=5)


class PerformanceFeedbackResponse(PerformanceFeedbackBase):
    id: uuid.UUID
    review_id: uuid.UUID
    submitted_by: uuid.UUID
    submitted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PerformanceReviewBase(BaseModel):
    overall_rating: float | None = Field(None, ge=0, le=5)
    overall_score: float | None = Field(None, ge=0, le=100)
    status: str = Field(default="Pending", max_length=50)


class PerformanceReviewCreate(PerformanceReviewBase):
    employee_id: uuid.UUID
    review_cycle_id: uuid.UUID
    reviewer_id: uuid.UUID


class PerformanceReviewUpdate(BaseModel):
    overall_rating: float | None = Field(None, ge=0, le=5)
    overall_score: float | None = Field(None, ge=0, le=100)
    status: str | None = Field(None, max_length=50)
    submitted_at: datetime | None = None


class PerformanceReviewResponse(PerformanceReviewBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    review_cycle_id: uuid.UUID
    reviewer_id: uuid.UUID
    submitted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    feedbacks: list[PerformanceFeedbackResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Competency & Employee Competency Schemas ---
class CompetencyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    category: str = Field(default="Core", max_length=100)


class CompetencyCreate(CompetencyBase):
    organization_id: uuid.UUID


class CompetencyUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    category: str | None = Field(None, max_length=100)


class CompetencyResponse(CompetencyBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeCompetencyBase(BaseModel):
    rating: float = Field(default=1.0, ge=1, le=5)
    verified: bool = Field(default=False)


class EmployeeCompetencyCreate(EmployeeCompetencyBase):
    employee_id: uuid.UUID
    competency_id: uuid.UUID


class EmployeeCompetencyUpdate(BaseModel):
    rating: float | None = Field(None, ge=1, le=5)
    verified: bool | None = None


class EmployeeCompetencyResponse(EmployeeCompetencyBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    competency_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Training Course & Program Schemas ---
class TrainingCourseBase(BaseModel):
    course_name: str = Field(..., min_length=1, max_length=255)
    course_code: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(None, max_length=2000)
    duration_hours: float = Field(default=1.0, ge=0.1)
    difficulty: str = Field(default="Intermediate", max_length=50)
    category: str = Field(default="General", max_length=100)
    status: str = Field(default="Active", max_length=50)


class TrainingCourseCreate(TrainingCourseBase):
    organization_id: uuid.UUID


class TrainingCourseUpdate(BaseModel):
    course_name: str | None = Field(None, min_length=1, max_length=255)
    course_code: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, max_length=2000)
    duration_hours: float | None = Field(None, ge=0.1)
    difficulty: str | None = Field(None, max_length=50)
    category: str | None = Field(None, max_length=100)
    status: str | None = Field(None, max_length=50)


class TrainingCourseResponse(TrainingCourseBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseEnrollmentBase(BaseModel):
    completion_percentage: float = Field(default=0.0, ge=0, le=100)
    status: str = Field(default="Enrolled", max_length=50)


class CourseEnrollmentCreate(BaseModel):
    employee_id: uuid.UUID
    course_id: uuid.UUID


class CourseEnrollmentUpdate(BaseModel):
    completion_percentage: float | None = Field(None, ge=0, le=100)
    status: str | None = Field(None, max_length=50)
    completed_at: datetime | None = None


class CourseEnrollmentResponse(CourseEnrollmentBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    course_id: uuid.UUID
    enrolled_at: datetime
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrainingProgramBase(BaseModel):
    program_name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    status: str = Field(default="Active", max_length=50)


class TrainingProgramCreate(TrainingProgramBase):
    organization_id: uuid.UUID
    course_ids: list[uuid.UUID] = Field(default_factory=list)


class TrainingProgramUpdate(BaseModel):
    program_name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    status: str | None = Field(None, max_length=50)


class TrainingProgramCourseResponse(BaseModel):
    id: uuid.UUID
    program_id: uuid.UUID
    course_id: uuid.UUID
    sequence: int

    model_config = ConfigDict(from_attributes=True)


class TrainingProgramResponse(TrainingProgramBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    program_courses: list[TrainingProgramCourseResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Certificate Schemas ---
class LearningCertificateBase(BaseModel):
    certificate_number: str = Field(..., max_length=100)
    issue_date: date
    expiry_date: date | None = None
    certificate_url: str | None = Field(None, max_length=500)


class LearningCertificateCreate(BaseModel):
    employee_id: uuid.UUID
    course_id: uuid.UUID
    issue_date: date | None = None
    expiry_date: date | None = None


class LearningCertificateResponse(LearningCertificateBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    course_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Skill Matrix Schemas ---
class SkillMatrixBase(BaseModel):
    skill_name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(default="Technical", max_length=100)
    current_level: str = Field(default="Beginner", max_length=50)
    target_level: str = Field(default="Advanced", max_length=50)


class SkillMatrixCreate(SkillMatrixBase):
    employee_id: uuid.UUID


class SkillMatrixUpdate(BaseModel):
    category: str | None = Field(None, max_length=100)
    current_level: str | None = Field(None, max_length=50)
    target_level: str | None = Field(None, max_length=50)


class SkillMatrixResponse(SkillMatrixBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    last_updated: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Dashboard Summaries & Analytics ---
class PerformanceDashboardSummary(BaseModel):
    total_goals: int
    completed_goals: int
    average_goal_progress: float
    active_review_cycles: int
    pending_reviews: int
    average_performance_rating: float
    promotion_readiness_score: float
    performance_trends: list[dict[str, Any]]


class TrainingDashboardSummary(BaseModel):
    total_courses: int
    active_enrollments: int
    completed_courses: int
    total_certificates: int
    avg_learning_progress: float
    skills_tracked: int
    skill_gap_percentage: float
