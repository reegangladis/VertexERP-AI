import uuid
from typing import Sequence
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.training_v9 import (
    Assessment,
    AssessmentAttempt,
    CourseModule,
    EmployeeTraining,
    Instructor,
    LearningPath,
    LearningPathCourse,
    LmsEmployeeSkill,
    SkillMatrix,
    TrainingCertification,
    TrainingCourse,
    TrainingSession,
)


class TrainingCourseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, course: TrainingCourse) -> TrainingCourse:
        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)
        return course

    async def get_by_id(self, course_id: uuid.UUID) -> TrainingCourse | None:
        stmt = (
            select(TrainingCourse)
            .options(
                selectinload(TrainingCourse.modules),
                selectinload(TrainingCourse.assessments),
            )
            .where(and_(TrainingCourse.id == course_id, TrainingCourse.is_deleted == False))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(self, org_id: uuid.UUID) -> Sequence[TrainingCourse]:
        stmt = (
            select(TrainingCourse)
            .options(
                selectinload(TrainingCourse.modules),
                selectinload(TrainingCourse.assessments),
            )
            .where(and_(TrainingCourse.organization_id == org_id, TrainingCourse.is_deleted == False))
            .order_by(TrainingCourse.course_name.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def create_module(self, module: CourseModule) -> CourseModule:
        self.db.add(module)
        await self.db.commit()
        await self.db.refresh(module)
        return module


class LearningPathRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, path: LearningPath) -> LearningPath:
        self.db.add(path)
        await self.db.commit()
        await self.db.refresh(path)
        return path

    async def get_by_id(self, path_id: uuid.UUID) -> LearningPath | None:
        stmt = (
            select(LearningPath)
            .options(selectinload(LearningPath.path_courses))
            .where(and_(LearningPath.id == path_id, LearningPath.is_deleted == False))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(self, org_id: uuid.UUID) -> Sequence[LearningPath]:
        stmt = (
            select(LearningPath)
            .options(selectinload(LearningPath.path_courses))
            .where(and_(LearningPath.organization_id == org_id, LearningPath.is_deleted == False))
            .order_by(LearningPath.path_name.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()


class EmployeeTrainingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, training: EmployeeTraining) -> EmployeeTraining:
        self.db.add(training)
        await self.db.commit()
        await self.db.refresh(training)
        return training

    async def get_by_id(self, training_id: uuid.UUID) -> EmployeeTraining | None:
        stmt = (
            select(EmployeeTraining)
            .options(selectinload(EmployeeTraining.certifications))
            .where(and_(EmployeeTraining.id == training_id, EmployeeTraining.is_deleted == False))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_employee(self, employee_id: uuid.UUID) -> Sequence[EmployeeTraining]:
        stmt = (
            select(EmployeeTraining)
            .options(selectinload(EmployeeTraining.certifications))
            .where(and_(EmployeeTraining.employee_id == employee_id, EmployeeTraining.is_deleted == False))
            .order_by(EmployeeTraining.assigned_date.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, training: EmployeeTraining) -> EmployeeTraining:
        await self.db.commit()
        await self.db.refresh(training)
        return training


class CertificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, cert: TrainingCertification) -> TrainingCertification:
        self.db.add(cert)
        await self.db.commit()
        await self.db.refresh(cert)
        return cert

    async def list_by_training(self, training_id: uuid.UUID) -> Sequence[TrainingCertification]:
        stmt = select(TrainingCertification).where(
            and_(TrainingCertification.employee_training_id == training_id, TrainingCertification.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()


class AssessmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_assessment(self, assessment: Assessment) -> Assessment:
        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)
        return assessment

    async def get_assessment_by_id(self, assessment_id: uuid.UUID) -> Assessment | None:
        stmt = (
            select(Assessment)
            .options(selectinload(Assessment.attempts))
            .where(and_(Assessment.id == assessment_id, Assessment.is_deleted == False))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create_attempt(self, attempt: AssessmentAttempt) -> AssessmentAttempt:
        self.db.add(attempt)
        await self.db.commit()
        await self.db.refresh(attempt)
        return attempt

    async def count_attempts(self, assessment_id: uuid.UUID, employee_id: uuid.UUID) -> int:
        stmt = select(AssessmentAttempt).where(
            and_(
                AssessmentAttempt.assessment_id == assessment_id,
                AssessmentAttempt.employee_id == employee_id,
                AssessmentAttempt.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return len(res.scalars().all())


class InstructorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_instructor(self, instructor: Instructor) -> Instructor:
        self.db.add(instructor)
        await self.db.commit()
        await self.db.refresh(instructor)
        return instructor

    async def create_session(self, session_obj: TrainingSession) -> TrainingSession:
        self.db.add(session_obj)
        await self.db.commit()
        await self.db.refresh(session_obj)
        return session_obj

    async def list_sessions(self, course_id: uuid.UUID) -> Sequence[TrainingSession]:
        stmt = (
            select(TrainingSession)
            .where(and_(TrainingSession.course_id == course_id, TrainingSession.is_deleted == False))
            .order_by(TrainingSession.session_date.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()


class SkillRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_employee_skill(self, skill: LmsEmployeeSkill) -> LmsEmployeeSkill:
        self.db.add(skill)
        await self.db.commit()
        await self.db.refresh(skill)
        return skill

    async def list_employee_skills(self, employee_id: uuid.UUID) -> Sequence[LmsEmployeeSkill]:
        stmt = (
            select(LmsEmployeeSkill)
            .where(and_(LmsEmployeeSkill.employee_id == employee_id, LmsEmployeeSkill.is_deleted == False))
            .order_by(LmsEmployeeSkill.skill_name.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def create_skill_matrix(self, matrix: SkillMatrix) -> SkillMatrix:
        self.db.add(matrix)
        await self.db.commit()
        await self.db.refresh(matrix)
        return matrix

    async def list_skill_matrix(self, org_id: uuid.UUID) -> Sequence[SkillMatrix]:
        stmt = (
            select(SkillMatrix)
            .where(and_(SkillMatrix.organization_id == org_id, SkillMatrix.is_deleted == False))
            .order_by(SkillMatrix.required_skill.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()
