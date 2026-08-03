import uuid
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.performance_learning_v9 import (
    Competency,
    CourseEnrollment,
    EmployeeCompetency,
    Goal,
    KeyResult,
    LearningCertificate,
    PerformanceFeedback,
    PerformanceReview,
    PerformanceReviewCycle,
    Phase9SkillMatrix,
    Phase9TrainingCourse,
    TrainingProgram,
    TrainingProgramCourse,
)
from app.repositories.base import BaseRepository


class GoalRepository(BaseRepository[Goal]):
    def __init__(self, db: AsyncSession):
        super().__init__(Goal, db)

    async def get_with_key_results(self, goal_id: uuid.UUID) -> Goal | None:
        stmt = (
            select(Goal)
            .options(selectinload(Goal.key_results))
            .where(Goal.id == goal_id, Goal.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_employee(self, employee_id: uuid.UUID) -> list[Goal]:
        stmt = (
            select(Goal)
            .options(selectinload(Goal.key_results))
            .where(Goal.employee_id == employee_id, Goal.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def find_duplicate_title(
        self, employee_id: uuid.UUID, title: str, exclude_id: uuid.UUID | None = None
    ) -> Goal | None:
        stmt = select(Goal).where(
            Goal.employee_id == employee_id,
            Goal.title == title,
            Goal.is_deleted == False,
        )
        if exclude_id:
            stmt = stmt.where(Goal.id != exclude_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class KeyResultRepository(BaseRepository[KeyResult]):
    def __init__(self, db: AsyncSession):
        super().__init__(KeyResult, db)

    async def get_by_goal(self, goal_id: uuid.UUID) -> list[KeyResult]:
        stmt = select(KeyResult).where(KeyResult.goal_id == goal_id, KeyResult.is_deleted == False)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class ReviewCycleRepository(BaseRepository[PerformanceReviewCycle]):
    def __init__(self, db: AsyncSession):
        super().__init__(PerformanceReviewCycle, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[PerformanceReviewCycle]:
        stmt = select(PerformanceReviewCycle).where(
            PerformanceReviewCycle.organization_id == org_id, PerformanceReviewCycle.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class PerformanceReviewRepository(BaseRepository[PerformanceReview]):
    def __init__(self, db: AsyncSession):
        super().__init__(PerformanceReview, db)

    async def get_with_feedback(self, review_id: uuid.UUID) -> PerformanceReview | None:
        stmt = (
            select(PerformanceReview)
            .options(selectinload(PerformanceReview.feedbacks))
            .where(PerformanceReview.id == review_id, PerformanceReview.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_employee(self, employee_id: uuid.UUID) -> list[PerformanceReview]:
        stmt = (
            select(PerformanceReview)
            .options(selectinload(PerformanceReview.feedbacks))
            .where(PerformanceReview.employee_id == employee_id, PerformanceReview.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class FeedbackRepository(BaseRepository[PerformanceFeedback]):
    def __init__(self, db: AsyncSession):
        super().__init__(PerformanceFeedback, db)

    async def get_by_review(self, review_id: uuid.UUID) -> list[PerformanceFeedback]:
        stmt = select(PerformanceFeedback).where(
            PerformanceFeedback.review_id == review_id, PerformanceFeedback.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class CompetencyRepository(BaseRepository[Competency]):
    def __init__(self, db: AsyncSession):
        super().__init__(Competency, db)

    async def find_duplicate_name(
        self, org_id: uuid.UUID, name: str, exclude_id: uuid.UUID | None = None
    ) -> Competency | None:
        stmt = select(Competency).where(
            Competency.organization_id == org_id,
            Competency.name == name,
            Competency.is_deleted == False,
        )
        if exclude_id:
            stmt = stmt.where(Competency.id != exclude_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class EmployeeCompetencyRepository(BaseRepository[EmployeeCompetency]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmployeeCompetency, db)

    async def get_by_employee(self, employee_id: uuid.UUID) -> list[EmployeeCompetency]:
        stmt = select(EmployeeCompetency).where(
            EmployeeCompetency.employee_id == employee_id, EmployeeCompetency.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class CourseRepository(BaseRepository[Phase9TrainingCourse]):
    def __init__(self, db: AsyncSession):
        super().__init__(Phase9TrainingCourse, db)

    async def get_by_code(self, org_id: uuid.UUID, course_code: str) -> Phase9TrainingCourse | None:
        stmt = select(Phase9TrainingCourse).where(
            Phase9TrainingCourse.organization_id == org_id,
            Phase9TrainingCourse.course_code == course_code,
            Phase9TrainingCourse.is_deleted == False,
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class EnrollmentRepository(BaseRepository[CourseEnrollment]):
    def __init__(self, db: AsyncSession):
        super().__init__(CourseEnrollment, db)

    async def get_existing_enrollment(
        self, employee_id: uuid.UUID, course_id: uuid.UUID
    ) -> CourseEnrollment | None:
        stmt = select(CourseEnrollment).where(
            CourseEnrollment.employee_id == employee_id,
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.is_deleted == False,
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_employee(self, employee_id: uuid.UUID) -> list[CourseEnrollment]:
        stmt = select(CourseEnrollment).where(
            CourseEnrollment.employee_id == employee_id, CourseEnrollment.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class TrainingProgramRepository(BaseRepository[TrainingProgram]):
    def __init__(self, db: AsyncSession):
        super().__init__(TrainingProgram, db)

    async def get_with_courses(self, program_id: uuid.UUID) -> TrainingProgram | None:
        stmt = (
            select(TrainingProgram)
            .options(selectinload(TrainingProgram.program_courses))
            .where(TrainingProgram.id == program_id, TrainingProgram.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class ProgramCourseRepository(BaseRepository[TrainingProgramCourse]):
    def __init__(self, db: AsyncSession):
        super().__init__(TrainingProgramCourse, db)


class CertificateRepository(BaseRepository[LearningCertificate]):
    def __init__(self, db: AsyncSession):
        super().__init__(LearningCertificate, db)

    async def get_by_employee(self, employee_id: uuid.UUID) -> list[LearningCertificate]:
        stmt = select(LearningCertificate).where(
            LearningCertificate.employee_id == employee_id, LearningCertificate.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_by_number(self, cert_number: str) -> LearningCertificate | None:
        stmt = select(LearningCertificate).where(
            LearningCertificate.certificate_number == cert_number, LearningCertificate.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class SkillMatrixRepository(BaseRepository[Phase9SkillMatrix]):
    def __init__(self, db: AsyncSession):
        super().__init__(Phase9SkillMatrix, db)

    async def get_by_employee(self, employee_id: uuid.UUID) -> list[Phase9SkillMatrix]:
        stmt = select(Phase9SkillMatrix).where(
            Phase9SkillMatrix.employee_id == employee_id, Phase9SkillMatrix.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
