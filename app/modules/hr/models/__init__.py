"""HR module ORM models package."""

from app.modules.hr.models.attendance import (
    AttendanceRecord,
    AttendanceRegularization,
    Shift,
    ShiftAssignment,
)
from app.modules.hr.models.employee import Employee
from app.modules.hr.models.learning import (
    CourseEnrollment,
    CourseModule,
    EmployeeCertification,
    EmployeeSkill,
    TrainingCourse,
)
from app.modules.hr.models.leave import (
    LeaveBalance,
    LeavePolicy,
    LeaveRequest,
    LeaveType,
)
from app.modules.hr.models.lifecycle import (
    EmployeeLifecycleEvent,
    EmploymentContract,
    OnboardingTask,
)
from app.modules.hr.models.payroll import (
    EmployeeSalaryAssignment,
    PayrollRun,
    Payslip,
    PayslipLine,
    SalaryComponent,
    SalaryStructure,
    SalaryStructureItem,
)
from app.modules.hr.models.performance import (
    EmployeeGoal,
    PerformanceReview,
    PerformanceReviewPeriod,
)
from app.modules.hr.models.profile import (
    EmployeeAddress,
    EmployeeBankAccount,
    EmployeeDocument,
    EmployeeEmergencyContact,
    EmployeeProfile,
)
from app.modules.hr.models.recruitment import (
    InterviewFeedback,
    InterviewSchedule,
    JobApplicant,
    JobOffer,
    JobRequisition,
)

__all__ = [
    "Employee",
    "EmployeeProfile",
    "EmployeeEmergencyContact",
    "EmployeeAddress",
    "EmployeeBankAccount",
    "EmployeeDocument",
    "EmploymentContract",
    "EmployeeLifecycleEvent",
    "OnboardingTask",
    "Shift",
    "ShiftAssignment",
    "AttendanceRecord",
    "AttendanceRegularization",
    "LeaveType",
    "LeavePolicy",
    "LeaveBalance",
    "LeaveRequest",
    "SalaryComponent",
    "SalaryStructure",
    "SalaryStructureItem",
    "EmployeeSalaryAssignment",
    "PayrollRun",
    "Payslip",
    "PayslipLine",
    "JobRequisition",
    "JobApplicant",
    "InterviewSchedule",
    "InterviewFeedback",
    "JobOffer",
    "PerformanceReviewPeriod",
    "EmployeeGoal",
    "PerformanceReview",
    "TrainingCourse",
    "CourseModule",
    "CourseEnrollment",
    "EmployeeSkill",
    "EmployeeCertification",
]
