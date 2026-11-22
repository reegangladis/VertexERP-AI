"""Performance Management, Goals/OKRs, and Appraisals API endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.audit.services.audit_service import AuditService
from app.modules.hr.schemas.performance import (
    EmployeeGoalCreate,
    EmployeeGoalResponse,
    EmployeeGoalUpdate,
    PerformanceReviewCreate,
    PerformanceReviewFinalize,
    PerformanceReviewManagerSubmit,
    PerformanceReviewPeriodCreate,
    PerformanceReviewPeriodResponse,
    PerformanceReviewResponse,
    PerformanceReviewSelfSubmit,
)
from app.modules.hr.services.performance_service import PerformanceService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.modules.identity.models.user import User

router = APIRouter(prefix="/performance", tags=["HR Performance & Appraisals"])


# --------------------------------------------------------------------------
# Review Periods
# --------------------------------------------------------------------------
@router.post(
    "/periods",
    response_model=PerformanceReviewPeriodResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Review Period Cycle",
    dependencies=[Depends(require_permission(PermissionCode.HR_PERFORMANCE_WRITE.value))],
)
async def create_period(
    req: PerformanceReviewPeriodCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PerformanceReviewPeriodResponse:
    """Creates a performance appraisal period."""
    service = PerformanceService(db)
    period = await service.create_period(tenant_id, org_id, req)
    return PerformanceReviewPeriodResponse.model_validate(period)


@router.get(
    "/periods",
    response_model=list[PerformanceReviewPeriodResponse],
    status_code=status.HTTP_200_OK,
    summary="List Review Periods",
    dependencies=[Depends(require_permission(PermissionCode.HR_PERFORMANCE_READ.value))],
)
async def list_periods(
    status: str | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[PerformanceReviewPeriodResponse]:
    """Lists appraisal review cycles."""
    service = PerformanceService(db)
    periods = await service.list_periods(tenant_id, org_id, status)
    return [PerformanceReviewPeriodResponse.model_validate(p) for p in periods]


@router.get(
    "/periods/{period_id}",
    response_model=PerformanceReviewPeriodResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Review Period",
    dependencies=[Depends(require_permission(PermissionCode.HR_PERFORMANCE_READ.value))],
)
async def get_period(
    period_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> PerformanceReviewPeriodResponse:
    """Gets review period by ID."""
    service = PerformanceService(db)
    period = await service.get_period(period_id, tenant_id, org_id)
    return PerformanceReviewPeriodResponse.model_validate(period)


# --------------------------------------------------------------------------
# Employee Goals / OKRs
# --------------------------------------------------------------------------
@router.post(
    "/goals",
    response_model=EmployeeGoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Employee Goal / OKR",
    dependencies=[Depends(require_permission(PermissionCode.HR_PERFORMANCE_WRITE.value))],
)
async def create_goal(
    req: EmployeeGoalCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmployeeGoalResponse:
    """Creates a performance goal or OKR."""
    service = PerformanceService(db)
    goal = await service.create_goal(tenant_id, org_id, req)
    return EmployeeGoalResponse.model_validate(goal)


@router.put(
    "/goals/{goal_id}",
    response_model=EmployeeGoalResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Goal Progress / Rating",
    dependencies=[Depends(require_permission(PermissionCode.HR_PERFORMANCE_WRITE.value))],
)
async def update_goal(
    goal_id: uuid.UUID,
    req: EmployeeGoalUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmployeeGoalResponse:
    """Updates goal progress, status, or self/manager rating."""
    service = PerformanceService(db)
    goal = await service.update_goal(goal_id, tenant_id, org_id, req)
    return EmployeeGoalResponse.model_validate(goal)


@router.get(
    "/goals",
    response_model=list[EmployeeGoalResponse],
    status_code=status.HTTP_200_OK,
    summary="List Employee Goals",
    dependencies=[Depends(require_permission(PermissionCode.HR_PERFORMANCE_READ.value))],
)
async def list_goals(
    employee_id: uuid.UUID | None = None,
    review_period_id: uuid.UUID | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[EmployeeGoalResponse]:
    """Lists employee goals with optional filters."""
    service = PerformanceService(db)
    goals = await service.list_goals(tenant_id, org_id, employee_id, review_period_id)
    return [EmployeeGoalResponse.model_validate(g) for g in goals]


# --------------------------------------------------------------------------
# Performance Reviews / Appraisals
# --------------------------------------------------------------------------
@router.post(
    "/reviews",
    response_model=PerformanceReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initiate Performance Review",
    dependencies=[Depends(require_permission(PermissionCode.HR_PERFORMANCE_WRITE.value))],
)
async def create_review(
    req: PerformanceReviewCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PerformanceReviewResponse:
    """Initiates an appraisal review record."""
    service = PerformanceService(db)
    review = await service.create_review(tenant_id, org_id, req)
    return PerformanceReviewResponse.model_validate(review)


@router.put(
    "/reviews/{review_id}/self",
    response_model=PerformanceReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Self Review Assessment",
    dependencies=[Depends(require_permission(PermissionCode.HR_PERFORMANCE_WRITE.value))],
)
async def submit_self_review(
    review_id: uuid.UUID,
    req: PerformanceReviewSelfSubmit,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PerformanceReviewResponse:
    """Submits employee self-appraisal score and remarks."""
    service = PerformanceService(db)
    review = await service.submit_self_review(review_id, tenant_id, org_id, req)
    return PerformanceReviewResponse.model_validate(review)


@router.put(
    "/reviews/{review_id}/manager",
    response_model=PerformanceReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Manager Review Assessment",
    dependencies=[Depends(require_permission(PermissionCode.HR_PERFORMANCE_WRITE.value))],
)
async def submit_manager_review(
    review_id: uuid.UUID,
    req: PerformanceReviewManagerSubmit,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PerformanceReviewResponse:
    """Submits manager appraisal evaluation and recommendations."""
    service = PerformanceService(db)
    review = await service.submit_manager_review(review_id, tenant_id, org_id, current_user.id, req)
    return PerformanceReviewResponse.model_validate(review)


@router.put(
    "/reviews/{review_id}/finalize",
    response_model=PerformanceReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Finalize Performance Appraisal",
    dependencies=[Depends(require_permission(PermissionCode.HR_PERFORMANCE_WRITE.value))],
)
async def finalize_review(
    review_id: uuid.UUID,
    req: PerformanceReviewFinalize,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PerformanceReviewResponse:
    """Finalizes performance appraisal with final grade."""
    service = PerformanceService(db)
    review = await service.finalize_review(review_id, tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_PERFORMANCE_REVIEW_FINALIZED",
        description=f"Performance review '{review_id}' finalized with rating '{review.final_rating}' ({review.final_score})",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return PerformanceReviewResponse.model_validate(review)


@router.get(
    "/reviews",
    response_model=list[PerformanceReviewResponse],
    status_code=status.HTTP_200_OK,
    summary="List Performance Reviews",
    dependencies=[Depends(require_permission(PermissionCode.HR_PERFORMANCE_READ.value))],
)
async def list_reviews(
    employee_id: uuid.UUID | None = None,
    review_period_id: uuid.UUID | None = None,
    status: str | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[PerformanceReviewResponse]:
    """Lists performance reviews."""
    service = PerformanceService(db)
    reviews = await service.list_reviews(tenant_id, org_id, employee_id, review_period_id, status)
    return [PerformanceReviewResponse.model_validate(r) for r in reviews]
