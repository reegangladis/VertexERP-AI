import uuid
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


# --- Course & Module Schemas ---
class CourseModuleCreate(BaseModel):
    module_name: str = Field(..., max_length=255)
    module_order: int = Field(1, ge=1)
    duration_minutes: int = Field(30, ge=1)
    content_url: str | None = None
    description: str | None = None


class CourseModuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    module_name: str
    module_order: int
    duration_minutes: int
    content_url: str | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class TrainingCourseCreate(BaseModel):
    organization_id: uuid.UUID
    course_code: str = Field(..., max_length=50)
    course_name: str = Field(..., max_length=255)
    description: str | None = None
    category: str = "General"
    difficulty_level: str = "Intermediate"
    duration_hours: float = 1.0
    delivery_mode: Literal["Online", "Offline", "Hybrid", "Self-paced"] = "Online"


class AssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    assessment_name: str
    passing_score: float
    total_marks: float
    duration_minutes: int
    created_at: datetime
    updated_at: datetime


class TrainingCourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    course_code: str
    course_name: str
    description: str | None = None
    category: str
    difficulty_level: str
    duration_hours: float
    delivery_mode: str
    status: str
    modules: list[CourseModuleResponse] = []
    assessments: list[AssessmentResponse] = []
    created_at: datetime
    updated_at: datetime


# --- Learning Path Schemas ---
class LearningPathCourseCreate(BaseModel):
    course_id: uuid.UUID
    sequence_number: int = Field(1, ge=1)
    is_mandatory: bool = True


class LearningPathCreate(BaseModel):
    organization_id: uuid.UUID
    path_name: str = Field(..., max_length=255)
    description: str | None = None
    courses: list[LearningPathCourseCreate] = []


class LearningPathCourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    learning_path_id: uuid.UUID
    course_id: uuid.UUID
    sequence_number: int
    is_mandatory: bool


class LearningPathResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    path_name: str
    description: str | None = None
    status: str
    path_courses: list[LearningPathCourseResponse] = []
    created_at: datetime
    updated_at: datetime


# --- Employee Training & Certifications ---
class EmployeeTrainingAssign(BaseModel):
    employee_id: uuid.UUID
    course_id: uuid.UUID
    due_date: date | None = None


class EmployeeTrainingProgress(BaseModel):
    completion_percentage: float = Field(..., ge=0.0, le=100.0)


class CertificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_training_id: uuid.UUID
    certificate_number: str
    issued_date: date
    expiry_date: date | None = None
    certificate_url: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class EmployeeTrainingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    course_id: uuid.UUID
    assigned_date: date
    due_date: date | None = None
    completed_date: date | None = None
    completion_percentage: float
    status: str
    certifications: list[CertificationResponse] = []
    created_at: datetime
    updated_at: datetime


# --- Assessment & Attempts Schemas ---
class AssessmentCreate(BaseModel):
    course_id: uuid.UUID
    assessment_name: str = Field(..., max_length=255)
    passing_score: float = Field(70.0, ge=0.0, le=100.0)
    total_marks: float = Field(100.0, ge=1.0)
    duration_minutes: int = Field(30, ge=5)


class AssessmentSubmit(BaseModel):
    employee_id: uuid.UUID
    score: float = Field(..., ge=0.0)


class AssessmentAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    assessment_id: uuid.UUID
    employee_id: uuid.UUID
    score: float
    attempt_number: int
    passed: bool
    submitted_at: datetime
    created_at: datetime
    updated_at: datetime


# --- Instructors & Training Sessions ---
class InstructorCreate(BaseModel):
    organization_id: uuid.UUID
    employee_id: uuid.UUID | None = None
    specialization: str = Field(..., max_length=255)
    experience_years: float = 0.0
    bio: str | None = None


class InstructorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID | None = None
    specialization: str
    experience_years: float
    bio: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class TrainingSessionCreate(BaseModel):
    course_id: uuid.UUID
    instructor_id: uuid.UUID | None = None
    session_date: date
    start_time: str
    end_time: str
    venue: str | None = None
    meeting_link: str | None = None
    capacity: int = 30


class TrainingSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    instructor_id: uuid.UUID | None = None
    session_date: date
    start_time: str
    end_time: str
    venue: str | None = None
    meeting_link: str | None = None
    capacity: int
    created_at: datetime
    updated_at: datetime


# --- Employee Skills & Skill Matrix ---
class EmployeeSkillCreate(BaseModel):
    employee_id: uuid.UUID
    skill_name: str = Field(..., max_length=100)
    skill_level: Literal["Beginner", "Intermediate", "Advanced", "Expert"] = "Intermediate"
    verified: bool = False


class EmployeeSkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    skill_name: str
    skill_level: str
    verified: bool
    last_updated: date
    created_at: datetime
    updated_at: datetime


class SkillMatrixCreate(BaseModel):
    organization_id: uuid.UUID
    designation_id: uuid.UUID | None = None
    required_skill: str = Field(..., max_length=100)
    minimum_level: Literal["Beginner", "Intermediate", "Advanced", "Expert"] = "Intermediate"


class SkillMatrixResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    designation_id: uuid.UUID | None = None
    required_skill: str
    minimum_level: str
    created_at: datetime
    updated_at: datetime


# --- Dashboard Summary Schema ---
class TrainingDashboardSummary(BaseModel):
    assigned_courses_count: int
    completed_courses_count: int
    pending_courses_count: int
    certificates_earned_count: int
    total_learning_hours: float
    upcoming_sessions_count: int
    skill_compliance_rate: float
