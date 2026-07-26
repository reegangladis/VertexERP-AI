import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.employee import Employee, EmployeeProfile, EmployeeDocument, EmployeeNote
from app.models.attendance import Attendance
from app.models.leave import LeaveType, LeaveBalance, LeaveRequest
from app.models.payroll import SalaryStructure
from app.models.recruitment import RecruitmentJob, Candidate, Application, Interview
from app.models.performance import PerformanceReview, Goal
from app.models.training import TrainingCourse, TrainingRecord

class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self, db: AsyncSession):
        super().__init__(Employee, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Employee]:
        stmt = select(Employee).where(Employee.organization_id == org_id, Employee.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_code(self, org_id: uuid.UUID, code: str) -> Optional[Employee]:
        stmt = select(Employee).where(Employee.organization_id == org_id, Employee.employee_code == code, Employee.is_deleted == False)
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

    async def get_by_org(self, org_id: uuid.UUID) -> List[LeaveType]:
        stmt = select(LeaveType).where(LeaveType.organization_id == org_id, LeaveType.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

class LeaveBalanceRepository(BaseRepository[LeaveBalance]):
    def __init__(self, db: AsyncSession):
        super().__init__(LeaveBalance, db)

class LeaveRequestRepository(BaseRepository[LeaveRequest]):
    def __init__(self, db: AsyncSession):
        super().__init__(LeaveRequest, db)

class SalaryStructureRepository(BaseRepository[SalaryStructure]):
    def __init__(self, db: AsyncSession):
        super().__init__(SalaryStructure, db)

class RecruitmentJobRepository(BaseRepository[RecruitmentJob]):
    def __init__(self, db: AsyncSession):
        super().__init__(RecruitmentJob, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[RecruitmentJob]:
        stmt = select(RecruitmentJob).where(RecruitmentJob.organization_id == org_id, RecruitmentJob.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

class CandidateRepository(BaseRepository[Candidate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Candidate, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Candidate]:
        stmt = select(Candidate).where(Candidate.organization_id == org_id, Candidate.is_deleted == False)
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

    async def get_by_org(self, org_id: uuid.UUID) -> List[TrainingCourse]:
        stmt = select(TrainingCourse).where(TrainingCourse.organization_id == org_id, TrainingCourse.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

class TrainingRecordRepository(BaseRepository[TrainingRecord]):
    def __init__(self, db: AsyncSession):
        super().__init__(TrainingRecord, db)
