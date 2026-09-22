"""Learning & Development (LMS), Skills, and Certifications API endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.audit.services.audit_service import AuditService
from app.modules.hr.schemas.learning import (
    CourseEnrollmentCreate,
    CourseEnrollmentProgressUpdate,
    CourseEnrollmentResponse,
    CourseModuleResponse,
    EmployeeCertificationCreate,
    EmployeeCertificationResponse,
    EmployeeSkillCreate,
    EmployeeSkillResponse,
    TrainingCourseCreate,
    TrainingCourseResponse,
)
from app.modules.hr.services.learning_service import LearningService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.modules.identity.models.user import User

router = APIRouter(prefix="/learning", tags=["HR Learning & Development"])


# --------------------------------------------------------------------------
# Training Courses
# --------------------------------------------------------------------------
@router.post(
    "/courses",
    response_model=TrainingCourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Training Course",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEARNING_WRITE.value))],
)
async def create_course(
    req: TrainingCourseCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TrainingCourseResponse:
    """Creates a new course catalog item with syllabus modules."""
    service = LearningService(db)
    course, modules = await service.create_course(tenant_id, org_id, req)
    return TrainingCourseResponse(
        id=course.id,
        tenant_id=course.tenant_id,
        organization_id=course.organization_id,
        code=course.code,
        title=course.title,
        description=course.description,
        category=course.category,
        duration_hours=float(course.duration_hours),
        provider=course.provider,
        is_mandatory=course.is_mandatory,
        is_active=course.is_active,
        version=course.version,
        modules=[CourseModuleResponse.model_validate(m) for m in modules],
        created_at=course.created_at,
        updated_at=course.updated_at,
    )


@router.get(
    "/courses",
    response_model=list[TrainingCourseResponse],
    status_code=status.HTTP_200_OK,
    summary="List Training Courses",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEARNING_READ.value))],
)
async def list_courses(
    category: str | None = None,
    is_active: bool | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[TrainingCourseResponse]:
    """Lists training courses."""
    service = LearningService(db)
    courses = await service.list_courses(tenant_id, org_id, category, is_active)
    result = []
    for c in courses:
        _, modules = await service.get_course(c.id, tenant_id, org_id)
        result.append(
            TrainingCourseResponse(
                id=c.id,
                tenant_id=c.tenant_id,
                organization_id=c.organization_id,
                code=c.code,
                title=c.title,
                description=c.description,
                category=c.category,
                duration_hours=float(c.duration_hours),
                provider=c.provider,
                is_mandatory=c.is_mandatory,
                is_active=c.is_active,
                version=c.version,
                modules=[CourseModuleResponse.model_validate(m) for m in modules],
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )
    return result


@router.get(
    "/courses/{course_id}",
    response_model=TrainingCourseResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Course Details",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEARNING_READ.value))],
)
async def get_course(
    course_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> TrainingCourseResponse:
    """Gets course and syllabus details."""
    service = LearningService(db)
    course, modules = await service.get_course(course_id, tenant_id, org_id)
    return TrainingCourseResponse(
        id=course.id,
        tenant_id=course.tenant_id,
        organization_id=course.organization_id,
        code=course.code,
        title=course.title,
        description=course.description,
        category=course.category,
        duration_hours=float(course.duration_hours),
        provider=course.provider,
        is_mandatory=course.is_mandatory,
        is_active=course.is_active,
        version=course.version,
        modules=[CourseModuleResponse.model_validate(m) for m in modules],
        created_at=course.created_at,
        updated_at=course.updated_at,
    )


# --------------------------------------------------------------------------
# Course Enrollments
# --------------------------------------------------------------------------
@router.post(
    "/enrollments",
    response_model=CourseEnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll Employee in Course",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEARNING_WRITE.value))],
)
async def enroll_course(
    req: CourseEnrollmentCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CourseEnrollmentResponse:
    """Enrolls an employee into a training course."""
    service = LearningService(db)
    enrollment = await service.enroll_employee(tenant_id, org_id, req)
    return CourseEnrollmentResponse.model_validate(enrollment)


@router.put(
    "/enrollments/{enrollment_id}/progress",
    response_model=CourseEnrollmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Course Learning Progress",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEARNING_WRITE.value))],
)
async def update_course_progress(
    enrollment_id: uuid.UUID,
    req: CourseEnrollmentProgressUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CourseEnrollmentResponse:
    """Updates progress percentage and awards certification upon completion."""
    service = LearningService(db)
    enrollment = await service.update_progress(enrollment_id, tenant_id, org_id, req)

    if enrollment.status == "COMPLETED":
        await AuditService.log_security_event(
            session=db,
            event_type="HR_COURSE_COMPLETED",
            description=f"Course '{enrollment.course_id}' completed by employee '{enrollment.employee_id}'",
            severity="INFO",
            tenant_id=tenant_id,
            user_id=current_user.id,
        )

    return CourseEnrollmentResponse.model_validate(enrollment)


@router.get(
    "/enrollments/employee/{employee_id}",
    response_model=list[CourseEnrollmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Employee Enrollments",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEARNING_READ.value))],
)
async def list_employee_enrollments(
    employee_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[CourseEnrollmentResponse]:
    """Lists courses enrolled by an employee."""
    service = LearningService(db)
    enrollments = await service.list_enrollments_for_employee(employee_id, tenant_id, org_id)
    return [CourseEnrollmentResponse.model_validate(e) for e in enrollments]


# --------------------------------------------------------------------------
# Skills & Certifications
# --------------------------------------------------------------------------
@router.post(
    "/skills",
    response_model=EmployeeSkillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record Employee Skill",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEARNING_WRITE.value))],
)
async def add_employee_skill(
    req: EmployeeSkillCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmployeeSkillResponse:
    """Records an employee skill."""
    service = LearningService(db)
    skill = await service.add_skill(tenant_id, org_id, req)
    return EmployeeSkillResponse.model_validate(skill)


@router.get(
    "/skills/employee/{employee_id}",
    response_model=list[EmployeeSkillResponse],
    status_code=status.HTTP_200_OK,
    summary="List Employee Skills",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEARNING_READ.value))],
)
async def list_employee_skills(
    employee_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[EmployeeSkillResponse]:
    """Lists skills recorded for an employee."""
    service = LearningService(db)
    skills = await service.list_skills(employee_id, tenant_id, org_id)
    return [EmployeeSkillResponse.model_validate(s) for s in skills]


@router.post(
    "/certifications",
    response_model=EmployeeCertificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record Employee Certification",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEARNING_WRITE.value))],
)
async def add_employee_certification(
    req: EmployeeCertificationCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmployeeCertificationResponse:
    """Records an employee professional credential or certification."""
    service = LearningService(db)
    cert = await service.add_certification(tenant_id, org_id, req)
    return EmployeeCertificationResponse.model_validate(cert)


@router.get(
    "/certifications/employee/{employee_id}",
    response_model=list[EmployeeCertificationResponse],
    status_code=status.HTTP_200_OK,
    summary="List Employee Certifications",
    dependencies=[Depends(require_permission(PermissionCode.HR_LEARNING_READ.value))],
)
async def list_employee_certifications(
    employee_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[EmployeeCertificationResponse]:
    """Lists certifications recorded for an employee."""
    service = LearningService(db)
    certs = await service.list_certifications(employee_id, tenant_id, org_id)
    return [EmployeeCertificationResponse.model_validate(c) for c in certs]
