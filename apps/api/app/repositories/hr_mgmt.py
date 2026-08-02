import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import Attendance
from app.models.employee import (
    Employee,
    EmployeeDocument,
    EmployeeNote,
    EmployeeProfile,
)
from app.models.leave import LeaveBalance, LeaveRequest, LeaveType
from app.models.payroll import SalaryStructure
from app.models.performance import Goal, PerformanceReview
from app.models.recruitment import Application, Candidate, Interview, RecruitmentJob
from app.models.training import TrainingCourse, TrainingRecord
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self, db: AsyncSession):
        super().__init__(Employee, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Employee]:
        stmt = select(Employee).where(
            Employee.organization_id == org_id, Employee.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_code(self, org_id: uuid.UUID, code: str) -> Employee | None:
        stmt = select(Employee).where(
            Employee.organization_id == org_id,
            Employee.employee_code == code,
            Employee.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class EmployeeProfileRepository(BaseRepository[EmployeeProfile]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmployeeProfile, db)


class EmployeeDocumentRepository(BaseRepository[EmployeeDocument]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmployeeDocument, db)


class EmployeeNoteRepository(BaseRepository[EmployeeNote]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmployeeNote, db)


class AttendanceRepository(BaseRepository[Attendance]):
    def __init__(self, db: AsyncSession):
        super().__init__(Attendance, db)


class LeaveTypeRepository(BaseRepository[LeaveType]):
    def __init__(self, db: AsyncSession):
        super().__init__(LeaveType, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[LeaveType]:
        stmt = select(LeaveType).where(
            LeaveType.organization_id == org_id, LeaveType.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class LeaveBalanceRepository(BaseRepository[LeaveBalance]):
    def __init__(self, db: AsyncSession):
        super().__init__(LeaveBalance, db)


class LeaveRequestRepository(BaseRepository[LeaveRequest]):
    def __init__(self, db: AsyncSession):
        super().__init__(LeaveRequest, db)


from app.models.payroll import PayrollRun, Payslip


class SalaryStructureRepository(BaseRepository[SalaryStructure]):
    def __init__(self, db: AsyncSession):
        super().__init__(SalaryStructure, db)


class PayrollRunRepository(BaseRepository[PayrollRun]):
    def __init__(self, db: AsyncSession):
        super().__init__(PayrollRun, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[PayrollRun]:
        stmt = (
            select(PayrollRun)
            .where(PayrollRun.organization_id == org_id, PayrollRun.is_deleted == False)
            .order_by(PayrollRun.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_period(
        self, org_id: uuid.UUID, month: int, year: int
    ) -> PayrollRun | None:
        stmt = select(PayrollRun).where(
            PayrollRun.organization_id == org_id,
            PayrollRun.period_month == month,
            PayrollRun.period_year == year,
            PayrollRun.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class PayslipRepository(BaseRepository[Payslip]):
    def __init__(self, db: AsyncSession):
        super().__init__(Payslip, db)

    async def get_by_payroll_run(self, run_id: uuid.UUID) -> list[Payslip]:
        stmt = select(Payslip).where(
            Payslip.payroll_run_id == run_id, Payslip.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class RecruitmentJobRepository(BaseRepository[RecruitmentJob]):
    def __init__(self, db: AsyncSession):
        super().__init__(RecruitmentJob, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[RecruitmentJob]:
        stmt = select(RecruitmentJob).where(
            RecruitmentJob.organization_id == org_id, RecruitmentJob.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class CandidateRepository(BaseRepository[Candidate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Candidate, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Candidate]:
        stmt = select(Candidate).where(
            Candidate.organization_id == org_id, Candidate.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class ApplicationRepository(BaseRepository[Application]):
    def __init__(self, db: AsyncSession):
        super().__init__(Application, db)


class InterviewRepository(BaseRepository[Interview]):
    def __init__(self, db: AsyncSession):
        super().__init__(Interview, db)


class PerformanceReviewRepository(BaseRepository[PerformanceReview]):
    def __init__(self, db: AsyncSession):
        super().__init__(PerformanceReview, db)


class GoalRepository(BaseRepository[Goal]):
    def __init__(self, db: AsyncSession):
        super().__init__(Goal, db)


class TrainingCourseRepository(BaseRepository[TrainingCourse]):
    def __init__(self, db: AsyncSession):
        super().__init__(TrainingCourse, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[TrainingCourse]:
        stmt = select(TrainingCourse).where(
            TrainingCourse.organization_id == org_id, TrainingCourse.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class TrainingRecordRepository(BaseRepository[TrainingRecord]):
    def __init__(self, db: AsyncSession):
        super().__init__(TrainingRecord, db)
