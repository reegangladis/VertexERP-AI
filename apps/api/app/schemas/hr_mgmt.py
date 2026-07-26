import uuid
from datetime import date, datetime
from typing import List, Optional, Any
from pydantic import BaseModel

# Base config class matching style of Phase 3
class HRBaseModel(BaseModel):
    class Config:
        from_attributes = True

# 1. Employee Schemas
class EmployeeProfileBase(HRBaseModel):
    personal_email: Optional[str] = None
    personal_phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    blood_group: Optional[str] = None
    nationality: Optional[str] = None
    passport_number: Optional[str] = None
    national_id: Optional[str] = None
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None
    emergency_contacts: Optional[List[dict]] = None
    photo_url: Optional[str] = None

class EmployeeProfileCreate(EmployeeProfileBase):
    pass

class EmployeeProfileResponse(EmployeeProfileBase):
    id: uuid.UUID
    employee_id: uuid.UUID

class EmployeeBase(HRBaseModel):
    employee_code: str
    employment_type: str = "full-time"
    status: str = "active"
    date_joined: date
    date_terminated: Optional[date] = None
    branch_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    designation_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None

class EmployeeCreate(EmployeeBase):
    profile: Optional[EmployeeProfileCreate] = None

class EmployeeUpdate(HRBaseModel):
    employment_type: Optional[str] = None
    status: Optional[str] = None
    date_terminated: Optional[date] = None
    branch_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    designation_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    profile: Optional[EmployeeProfileCreate] = None

class EmployeeResponse(EmployeeBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    profile: Optional[EmployeeProfileResponse] = None

# 2. Attendance Schemas
class AttendanceBase(HRBaseModel):
    date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    total_hours: float = 0.0
    status: str = "present"
    is_late_arrival: bool = False
    is_early_exit: bool = False
    overtime_minutes: int = 0
    total_break_minutes: int = 0

class AttendanceCreate(AttendanceBase):
    employee_id: uuid.UUID

class AttendanceResponse(AttendanceBase):
    id: uuid.UUID
    employee_id: uuid.UUID

class CheckInRequest(HRBaseModel):
    employee_id: uuid.UUID
    check_in_time: Optional[datetime] = None

class CheckOutRequest(HRBaseModel):
    employee_id: uuid.UUID
    check_out_time: Optional[datetime] = None

# 3. Leave Schemas
class LeaveTypeBase(HRBaseModel):
    name: str
    code: str
    days_per_year: float
    is_carry_forward: bool = False

class LeaveTypeCreate(LeaveTypeBase):
    pass

class LeaveTypeResponse(LeaveTypeBase):
    id: uuid.UUID
    organization_id: uuid.UUID

class LeaveBalanceResponse(HRBaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    leave_type_id: uuid.UUID
    leave_type_name: Optional[str] = None
    leave_type_code: Optional[str] = None
    year: int
    allocated: float
    used: float
    remaining: float

class LeaveRequestBase(HRBaseModel):
    leave_type_id: uuid.UUID
    start_date: date
    end_date: date
    reason: str

class LeaveRequestCreate(LeaveRequestBase):
    employee_id: uuid.UUID

class LeaveRequestUpdate(HRBaseModel):
    status: str # approved, rejected, cancelled
    approval_comment: Optional[str] = None

class LeaveRequestResponse(HRBaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    leave_type_id: uuid.UUID
    start_date: date
    end_date: date
    total_days: float
    reason: str
    status: str
    approved_by_id: Optional[uuid.UUID] = None
    approval_comment: Optional[str] = None

# 4. Salary Structure Schemas (Payroll)
class SalaryStructureBase(HRBaseModel):
    base_salary: float
    allowances: Optional[dict] = None
    deductions: Optional[dict] = None
    benefits: Optional[dict] = None
    effective_from: date
    effective_to: Optional[date] = None

class SalaryStructureCreate(SalaryStructureBase):
    employee_id: uuid.UUID

class SalaryStructureResponse(SalaryStructureBase):
    id: uuid.UUID
    employee_id: uuid.UUID

# 5. Recruitment Schemas
class RecruitmentJobBase(HRBaseModel):
    title: str
    description: str
    requirements: Optional[str] = None
    department_id: Optional[uuid.UUID] = None
    location_id: Optional[uuid.UUID] = None
    employment_type: str = "full-time"
    status: str = "published"

class RecruitmentJobCreate(RecruitmentJobBase):
    pass

class RecruitmentJobResponse(RecruitmentJobBase):
    id: uuid.UUID
    organization_id: uuid.UUID

class CandidateBase(HRBaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    headline: Optional[str] = None
    skills: Optional[List[str]] = None

class CandidateCreate(CandidateBase):
    pass

class CandidateResponse(CandidateBase):
    id: uuid.UUID
    organization_id: uuid.UUID

class ApplicationBase(HRBaseModel):
    job_id: uuid.UUID
    candidate_id: uuid.UUID
    stage: str = "applied"
    status: str = "active"
    offer_details: Optional[dict] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(HRBaseModel):
    stage: str
    status: Optional[str] = None
    offer_details: Optional[dict] = None

class ApplicationResponse(ApplicationBase):
    id: uuid.UUID
    candidate_name: Optional[str] = None
    job_title: Optional[str] = None

class InterviewBase(HRBaseModel):
    application_id: uuid.UUID
    interviewers: Optional[List[str]] = None
    scheduled_at: datetime
    stage: str
    feedback: Optional[str] = None
    rating: Optional[int] = None
    status: str = "scheduled"

class InterviewCreate(InterviewBase):
    pass

class InterviewResponse(InterviewBase):
    id: uuid.UUID

# 6. Performance Schemas
class GoalBase(HRBaseModel):
    title: str
    description: Optional[str] = None
    kpi_metrics: Optional[str] = None
    target_date: date
    progress: int = 0
    status: str = "not_started"

class GoalCreate(GoalBase):
    employee_id: uuid.UUID

class GoalResponse(GoalBase):
    id: uuid.UUID
    employee_id: uuid.UUID

class PerformanceReviewBase(HRBaseModel):
    reviewer_id: uuid.UUID
    review_cycle: str
    rating: Optional[float] = None
    manager_feedback: Optional[str] = None
    peer_feedback: Optional[List[dict]] = None
    self_assessment: Optional[str] = None
    status: str = "submitted"

class PerformanceReviewCreate(PerformanceReviewBase):
    employee_id: uuid.UUID

class PerformanceReviewResponse(PerformanceReviewBase):
    id: uuid.UUID
    employee_id: uuid.UUID

# 7. Training Schemas
class TrainingCourseBase(HRBaseModel):
    title: str
    description: Optional[str] = None
    instructor: Optional[str] = None
    duration_hours: float = 0.0

class TrainingCourseCreate(TrainingCourseBase):
    pass

class TrainingCourseResponse(TrainingCourseBase):
    id: uuid.UUID
    organization_id: uuid.UUID

class TrainingRecordBase(HRBaseModel):
    course_id: uuid.UUID
    status: str = "assigned"
    progress: int = 0
    certificate_url: Optional[str] = None
    completed_at: Optional[date] = None

class TrainingRecordCreate(TrainingRecordBase):
    employee_id: uuid.UUID

class TrainingRecordResponse(TrainingRecordBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    course_title: Optional[str] = None

# 8. Document & Note Schemas
class EmployeeDocumentResponse(HRBaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    name: str
    type: str
    file_path: str
    file_size: int
    mime_type: str
    storage_provider: str

class EmployeeNoteCreate(HRBaseModel):
    employee_id: uuid.UUID
    content: str
    is_private: bool = False

class EmployeeNoteResponse(HRBaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    author_id: uuid.UUID
    content: str
    is_private: bool
    created_at: datetime
