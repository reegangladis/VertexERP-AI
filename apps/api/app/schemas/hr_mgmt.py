import uuid
from datetime import date, datetime

from pydantic import BaseModel


# Base config class matching style of Phase 3
class HRBaseModel(BaseModel):
    class Config:
        from_attributes = True


# 1. Employee Schemas
class EmployeeProfileBase(HRBaseModel):
    personal_email: str | None = None
    personal_phone: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    marital_status: str | None = None
    blood_group: str | None = None
    nationality: str | None = None
    passport_number: str | None = None
    national_id: str | None = None
    current_address: str | None = None
    permanent_address: str | None = None
    emergency_contacts: list[dict] | None = None
    photo_url: str | None = None


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
    date_terminated: date | None = None
    branch_id: uuid.UUID | None = None
    department_id: uuid.UUID | None = None
    designation_id: uuid.UUID | None = None
    manager_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None


class EmployeeCreate(EmployeeBase):
    profile: EmployeeProfileCreate | None = None


class EmployeeUpdate(HRBaseModel):
    employment_type: str | None = None
    status: str | None = None
    date_terminated: date | None = None
    branch_id: uuid.UUID | None = None
    department_id: uuid.UUID | None = None
    designation_id: uuid.UUID | None = None
    manager_id: uuid.UUID | None = None
    profile: EmployeeProfileCreate | None = None


class EmployeeResponse(EmployeeBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    profile: EmployeeProfileResponse | None = None


# 2. Attendance Schemas
class AttendanceBase(HRBaseModel):
    date: date
    check_in: datetime | None = None
    check_out: datetime | None = None
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
    check_in_time: datetime | None = None


class CheckOutRequest(HRBaseModel):
    employee_id: uuid.UUID
    check_out_time: datetime | None = None


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
    leave_type_name: str | None = None
    leave_type_code: str | None = None
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
    status: str  # approved, rejected, cancelled
    approval_comment: str | None = None


class LeaveRequestResponse(HRBaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    leave_type_id: uuid.UUID
    start_date: date
    end_date: date
    total_days: float
    reason: str
    status: str
    approved_by_id: uuid.UUID | None = None
    approval_comment: str | None = None


# 4. Salary Structure Schemas (Payroll)
class SalaryStructureBase(HRBaseModel):
    base_salary: float
    allowances: dict | None = None
    deductions: dict | None = None
    benefits: dict | None = None
    effective_from: date
    effective_to: date | None = None


class SalaryStructureCreate(SalaryStructureBase):
    employee_id: uuid.UUID


class SalaryStructureResponse(SalaryStructureBase):
    id: uuid.UUID
    employee_id: uuid.UUID


class PayrollRunProcessRequest(HRBaseModel):
    period_month: int
    period_year: int


class PayslipResponse(HRBaseModel):
    id: uuid.UUID
    payroll_run_id: uuid.UUID
    employee_id: uuid.UUID
    base_salary: float
    total_allowances: float
    total_deductions: float
    net_salary: float
    allowances_breakdown: dict | None = None
    deductions_breakdown: dict | None = None
    status: str


class PayrollRunResponse(HRBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    period_month: int
    period_year: int
    status: str
    total_gross: float
    total_deductions: float
    total_net: float
    processed_at: datetime | None = None
    payslips: list[PayslipResponse] | None = None


class EmployeeStatusUpdate(HRBaseModel):
    status: str  # active, suspended, terminated, onboarded, pending, archived
    date_terminated: date | None = None
    department_id: uuid.UUID | None = None
    designation_id: uuid.UUID | None = None
    branch_id: uuid.UUID | None = None


# 5. Recruitment Schemas
class RecruitmentJobBase(HRBaseModel):
    title: str
    description: str
    requirements: str | None = None
    department_id: uuid.UUID | None = None
    location_id: uuid.UUID | None = None
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
    phone: str | None = None
    resume_url: str | None = None
    headline: str | None = None
    skills: list[str] | None = None


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
    offer_details: dict | None = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(HRBaseModel):
    stage: str
    status: str | None = None
    offer_details: dict | None = None


class ApplicationResponse(ApplicationBase):
    id: uuid.UUID
    candidate_name: str | None = None
    job_title: str | None = None


class InterviewBase(HRBaseModel):
    application_id: uuid.UUID
    interviewers: list[str] | None = None
    scheduled_at: datetime
    stage: str
    feedback: str | None = None
    rating: int | None = None
    status: str = "scheduled"


class InterviewCreate(InterviewBase):
    pass


class InterviewResponse(InterviewBase):
    id: uuid.UUID


# 6. Performance Schemas
class GoalBase(HRBaseModel):
    title: str
    description: str | None = None
    kpi_metrics: str | None = None
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
    rating: float | None = None
    manager_feedback: str | None = None
    peer_feedback: list[dict] | None = None
    self_assessment: str | None = None
    status: str = "submitted"


class PerformanceReviewCreate(PerformanceReviewBase):
    employee_id: uuid.UUID


class PerformanceReviewResponse(PerformanceReviewBase):
    id: uuid.UUID
    employee_id: uuid.UUID


# 7. Training Schemas
class TrainingCourseBase(HRBaseModel):
    title: str
    description: str | None = None
    instructor: str | None = None
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
    certificate_url: str | None = None
    completed_at: date | None = None


class TrainingRecordCreate(TrainingRecordBase):
    employee_id: uuid.UUID


class TrainingRecordResponse(TrainingRecordBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    course_title: str | None = None


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
