"""Learning service."""

import uuid
from collections.abc import Sequence
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.hr.models.learning import (
    CourseEnrollment,
    CourseModule,
    EmployeeCertification,
    EmployeeSkill,
    TrainingCourse,
)
from app.modules.hr.repositories.employee_repository import EmployeeRepository
from app.modules.hr.repositories.learning_repository import LearningRepository
from app.modules.hr.schemas.learning import (
    CourseEnrollmentCreate,
    CourseEnrollmentProgressUpdate,
    EmployeeCertificationCreate,
    EmployeeSkillCreate,
    TrainingCourseCreate,
)


class LearningService:
    """Business service for Course Catalogs, Enrollments, Skills, and Certifications."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.learning_repo = LearningRepository(session)
        self.emp_repo = EmployeeRepository(session)

    # --------------------------------------------------------------------------
    # Courses & Modules
    # --------------------------------------------------------------------------
    async def create_course(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: TrainingCourseCreate
    ) -> tuple[TrainingCourse, Sequence[CourseModule]]:
        existing = await self.learning_repo.get_course_by_code(data.code, tenant_id, org_id)
        if existing:
            raise ConflictException(f"Training course with code '{data.code}' already exists")

        course = TrainingCourse(
            tenant_id=tenant_id,
            organization_id=org_id,
            code=data.code,
            title=data.title,
            description=data.description,
            category=data.category,
            duration_hours=Decimal(str(data.duration_hours)),
            provider=data.provider,
            is_mandatory=data.is_mandatory,
            is_active=data.is_active,
        )

        modules = [
            CourseModule(
                tenant_id=tenant_id,
                organization_id=org_id,
                title=m.title,
                sequence_order=m.sequence_order,
                content_type=m.content_type,
                content_url=m.content_url,
                duration_minutes=m.duration_minutes,
            )
            for m in data.modules
        ]

        saved = await self.learning_repo.create_course(course, modules)
        saved_modules = await self.learning_repo.get_course_modules(saved.id, tenant_id, org_id)
        return saved, saved_modules

    async def get_course(
        self, course_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> tuple[TrainingCourse, Sequence[CourseModule]]:
        course = await self.learning_repo.get_course(course_id, tenant_id, org_id)
        if not course:
            raise NotFoundException(f"Course '{course_id}' not found")
        modules = await self.learning_repo.get_course_modules(course.id, tenant_id, org_id)
        return course, modules

    async def list_courses(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        category: str | None = None,
        is_active: bool | None = None,
    ) -> Sequence[TrainingCourse]:
        return await self.learning_repo.list_courses(tenant_id, org_id, category, is_active)

    # --------------------------------------------------------------------------
    # Enrollments
    # --------------------------------------------------------------------------
    async def enroll_employee(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: CourseEnrollmentCreate
    ) -> CourseEnrollment:
        emp = await self.emp_repo.get_by_id(data.employee_id, tenant_id, org_id)
        if not emp:
            raise NotFoundException(f"Employee '{data.employee_id}' not found")

        course = await self.learning_repo.get_course(data.course_id, tenant_id, org_id)
        if not course:
            raise NotFoundException(f"Course '{data.course_id}' not found")

        enrollment = CourseEnrollment(
            tenant_id=tenant_id,
            organization_id=org_id,
            employee_id=data.employee_id,
            course_id=data.course_id,
            enrolled_date=date.today(),
            status="ENROLLED",
            progress_percentage=0,
        )
        return await self.learning_repo.create_enrollment(enrollment)

    async def update_progress(
        self,
        enrollment_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: CourseEnrollmentProgressUpdate,
    ) -> CourseEnrollment:
        enrollment = await self.learning_repo.get_enrollment(enrollment_id, tenant_id, org_id)
        if not enrollment:
            raise NotFoundException(f"Course enrollment '{enrollment_id}' not found")

        enrollment.progress_percentage = data.progress_percentage
        if data.score is not None:
            enrollment.score = Decimal(str(data.score))

        if data.progress_percentage >= 100:
            enrollment.status = "COMPLETED"
            enrollment.completion_date = date.today()
            enrollment.certificate_url = f"https://certs.vertexerp.io/verify/{enrollment.id}"
        elif data.progress_percentage > 0:
            enrollment.status = "IN_PROGRESS"

        enrollment.updated_at = datetime.now(UTC)
        return await self.learning_repo.update_enrollment(enrollment)

    async def list_enrollments_for_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[CourseEnrollment]:
        return await self.learning_repo.list_enrollments_for_employee(
            employee_id, tenant_id, org_id
        )

    # --------------------------------------------------------------------------
    # Skills & Certifications
    # --------------------------------------------------------------------------
    async def add_skill(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: EmployeeSkillCreate
    ) -> EmployeeSkill:
        emp = await self.emp_repo.get_by_id(data.employee_id, tenant_id, org_id)
        if not emp:
            raise NotFoundException(f"Employee '{data.employee_id}' not found")

        skill = EmployeeSkill(
            tenant_id=tenant_id,
            organization_id=org_id,
            employee_id=data.employee_id,
            skill_name=data.skill_name,
            proficiency_level=data.proficiency_level,
            years_of_experience=Decimal(str(data.years_of_experience)),
            is_verified=True,
        )
        return await self.learning_repo.create_skill(skill)

    async def list_skills(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmployeeSkill]:
        return await self.learning_repo.list_skills_for_employee(employee_id, tenant_id, org_id)

    async def add_certification(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: EmployeeCertificationCreate
    ) -> EmployeeCertification:
        emp = await self.emp_repo.get_by_id(data.employee_id, tenant_id, org_id)
        if not emp:
            raise NotFoundException(f"Employee '{data.employee_id}' not found")

        cert = EmployeeCertification(
            tenant_id=tenant_id,
            organization_id=org_id,
            employee_id=data.employee_id,
            certification_name=data.certification_name,
            issuing_organization=data.issuing_organization,
            issue_date=data.issue_date,
            expiry_date=data.expiry_date,
            credential_id=data.credential_id,
            credential_url=data.credential_url,
        )
        return await self.learning_repo.create_certification(cert)

    async def list_certifications(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmployeeCertification]:
        return await self.learning_repo.list_certifications_for_employee(
            employee_id, tenant_id, org_id
        )
