"""Learning repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hr.models.learning import (
    CourseEnrollment,
    CourseModule,
    EmployeeCertification,
    EmployeeSkill,
    TrainingCourse,
)


class LearningRepository:
    """PostgreSQL implementation of Learning & LMS repository with multi-tenant filtering."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # --------------------------------------------------------------------------
    # Training Courses & Modules
    # --------------------------------------------------------------------------
    async def create_course(
        self, course: TrainingCourse, modules: list[CourseModule]
    ) -> TrainingCourse:
        self.session.add(course)
        await self.session.flush()

        for m in modules:
            m.course_id = course.id
            self.session.add(m)

        await self.session.commit()
        await self.session.refresh(course)
        return course

    async def get_course(
        self, course_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> TrainingCourse | None:
        stmt = select(TrainingCourse).where(
            TrainingCourse.id == course_id,
            TrainingCourse.tenant_id == tenant_id,
            TrainingCourse.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_course_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> TrainingCourse | None:
        stmt = select(TrainingCourse).where(
            TrainingCourse.code == code,
            TrainingCourse.tenant_id == tenant_id,
            TrainingCourse.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_course_modules(
        self, course_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[CourseModule]:
        stmt = (
            select(CourseModule)
            .where(
                CourseModule.course_id == course_id,
                CourseModule.tenant_id == tenant_id,
                CourseModule.organization_id == org_id,
            )
            .order_by(CourseModule.sequence_order.asc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def add_module(self, module: CourseModule) -> CourseModule:
        self.session.add(module)
        await self.session.commit()
        await self.session.refresh(module)
        return module

    async def list_courses(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        category: str | None = None,
        is_active: bool | None = None,
    ) -> Sequence[TrainingCourse]:
        stmt = select(TrainingCourse).where(
            TrainingCourse.tenant_id == tenant_id,
            TrainingCourse.organization_id == org_id,
        )
        if category:
            stmt = stmt.where(TrainingCourse.category == category)
        if is_active is not None:
            stmt = stmt.where(TrainingCourse.is_active == is_active)
        stmt = stmt.order_by(TrainingCourse.title.asc())
        res = await self.session.execute(stmt)
        return res.scalars().all()

    # --------------------------------------------------------------------------
    # Course Enrollments
    # --------------------------------------------------------------------------
    async def create_enrollment(self, enrollment: CourseEnrollment) -> CourseEnrollment:
        self.session.add(enrollment)
        await self.session.commit()
        await self.session.refresh(enrollment)
        return enrollment

    async def get_enrollment(
        self, enrollment_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> CourseEnrollment | None:
        stmt = select(CourseEnrollment).where(
            CourseEnrollment.id == enrollment_id,
            CourseEnrollment.tenant_id == tenant_id,
            CourseEnrollment.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_enrollment(self, enrollment: CourseEnrollment) -> CourseEnrollment:
        await self.session.commit()
        await self.session.refresh(enrollment)
        return enrollment

    async def list_enrollments_for_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[CourseEnrollment]:
        stmt = (
            select(CourseEnrollment)
            .where(
                CourseEnrollment.employee_id == employee_id,
                CourseEnrollment.tenant_id == tenant_id,
                CourseEnrollment.organization_id == org_id,
            )
            .order_by(CourseEnrollment.enrolled_date.desc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    # --------------------------------------------------------------------------
    # Skills & Certifications
    # --------------------------------------------------------------------------
    async def create_skill(self, skill: EmployeeSkill) -> EmployeeSkill:
        self.session.add(skill)
        await self.session.commit()
        await self.session.refresh(skill)
        return skill

    async def list_skills_for_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmployeeSkill]:
        stmt = (
            select(EmployeeSkill)
            .where(
                EmployeeSkill.employee_id == employee_id,
                EmployeeSkill.tenant_id == tenant_id,
                EmployeeSkill.organization_id == org_id,
            )
            .order_by(EmployeeSkill.skill_name.asc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def create_certification(self, cert: EmployeeCertification) -> EmployeeCertification:
        self.session.add(cert)
        await self.session.commit()
        await self.session.refresh(cert)
        return cert

    async def list_certifications_for_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmployeeCertification]:
        stmt = (
            select(EmployeeCertification)
            .where(
                EmployeeCertification.employee_id == employee_id,
                EmployeeCertification.tenant_id == tenant_id,
                EmployeeCertification.organization_id == org_id,
            )
            .order_by(EmployeeCertification.issue_date.desc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
