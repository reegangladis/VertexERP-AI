"""Performance service."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.hr.models.performance import (
    EmployeeGoal,
    PerformanceReview,
    PerformanceReviewPeriod,
)
from app.modules.hr.repositories.employee_repository import EmployeeRepository
from app.modules.hr.repositories.performance_repository import PerformanceRepository
from app.modules.hr.schemas.performance import (
    EmployeeGoalCreate,
    EmployeeGoalUpdate,
    PerformanceReviewCreate,
    PerformanceReviewFinalize,
    PerformanceReviewManagerSubmit,
    PerformanceReviewPeriodCreate,
    PerformanceReviewSelfSubmit,
)


class PerformanceService:
    """Business service for Performance Appraisal Cycles, Goals/OKRs, and Multi-stage Reviews."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.perf_repo = PerformanceRepository(session)
        self.emp_repo = EmployeeRepository(session)

    # --------------------------------------------------------------------------
    # Review Periods
    # --------------------------------------------------------------------------
    async def create_period(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: PerformanceReviewPeriodCreate
    ) -> PerformanceReviewPeriod:
        existing = await self.perf_repo.get_period_by_code(data.code, tenant_id, org_id)
        if existing:
            raise ConflictException(
                f"Performance review period with code '{data.code}' already exists"
            )

        period = PerformanceReviewPeriod(
            tenant_id=tenant_id,
            organization_id=org_id,
            code=data.code,
            title=data.title,
            start_date=data.start_date,
            end_date=data.end_date,
            self_review_deadline=data.self_review_deadline,
            manager_review_deadline=data.manager_review_deadline,
            status=data.status,
            is_active=data.is_active,
        )
        return await self.perf_repo.create_period(period)

    async def get_period(
        self, period_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> PerformanceReviewPeriod:
        period = await self.perf_repo.get_period(period_id, tenant_id, org_id)
        if not period:
            raise NotFoundException(f"Performance review period '{period_id}' not found")
        return period

    async def list_periods(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, status: str | None = None
    ) -> Sequence[PerformanceReviewPeriod]:
        return await self.perf_repo.list_periods(tenant_id, org_id, status)

    # --------------------------------------------------------------------------
    # Employee Goals
    # --------------------------------------------------------------------------
    async def create_goal(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: EmployeeGoalCreate
    ) -> EmployeeGoal:
        emp = await self.emp_repo.get_by_id(data.employee_id, tenant_id, org_id)
        if not emp:
            raise NotFoundException(f"Employee '{data.employee_id}' not found")

        if data.review_period_id:
            period = await self.perf_repo.get_period(data.review_period_id, tenant_id, org_id)
            if not period:
                raise NotFoundException(f"Review period '{data.review_period_id}' not found")

        goal = EmployeeGoal(
            tenant_id=tenant_id,
            organization_id=org_id,
            employee_id=data.employee_id,
            review_period_id=data.review_period_id,
            title=data.title,
            description=data.description,
            category=data.category,
            weightage=Decimal(str(data.weightage)),
            target_date=data.target_date,
            progress_percentage=0,
            status="NOT_STARTED",
        )
        return await self.perf_repo.create_goal(goal)

    async def update_goal(
        self, goal_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, data: EmployeeGoalUpdate
    ) -> EmployeeGoal:
        goal = await self.perf_repo.get_goal(goal_id, tenant_id, org_id)
        if not goal:
            raise NotFoundException(f"Goal '{goal_id}' not found")

        if data.title is not None:
            goal.title = data.title
        if data.description is not None:
            goal.description = data.description
        if data.progress_percentage is not None:
            goal.progress_percentage = data.progress_percentage
            if data.progress_percentage >= 100:
                goal.status = "ACHIEVED"
            elif data.progress_percentage > 0 and goal.status == "NOT_STARTED":
                goal.status = "IN_PROGRESS"
        if data.status is not None:
            goal.status = data.status
        if data.self_rating is not None:
            goal.self_rating = Decimal(str(data.self_rating))
        if data.manager_rating is not None:
            goal.manager_rating = Decimal(str(data.manager_rating))

        goal.updated_at = datetime.now(UTC)
        return await self.perf_repo.update_goal(goal)

    async def get_goal(
        self, goal_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> EmployeeGoal:
        goal = await self.perf_repo.get_goal(goal_id, tenant_id, org_id)
        if not goal:
            raise NotFoundException(f"Goal '{goal_id}' not found")
        return goal

    async def list_goals(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        employee_id: uuid.UUID | None = None,
        review_period_id: uuid.UUID | None = None,
    ) -> Sequence[EmployeeGoal]:
        return await self.perf_repo.list_goals(tenant_id, org_id, employee_id, review_period_id)

    # --------------------------------------------------------------------------
    # Performance Reviews
    # --------------------------------------------------------------------------
    async def create_review(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: PerformanceReviewCreate
    ) -> PerformanceReview:
        emp = await self.emp_repo.get_by_id(data.employee_id, tenant_id, org_id)
        if not emp:
            raise NotFoundException(f"Employee '{data.employee_id}' not found")

        period = await self.perf_repo.get_period(data.review_period_id, tenant_id, org_id)
        if not period:
            raise NotFoundException(f"Review period '{data.review_period_id}' not found")

        review = PerformanceReview(
            tenant_id=tenant_id,
            organization_id=org_id,
            employee_id=data.employee_id,
            reviewer_id=data.reviewer_id,
            review_period_id=data.review_period_id,
            status="SELF_REVIEW",
            promotion_recommendation=False,
        )
        return await self.perf_repo.create_review(review)

    async def submit_self_review(
        self,
        review_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: PerformanceReviewSelfSubmit,
    ) -> PerformanceReview:
        review = await self.perf_repo.get_review(review_id, tenant_id, org_id)
        if not review:
            raise NotFoundException(f"Performance review '{review_id}' not found")

        review.self_score = Decimal(str(data.self_score))
        if data.strengths:
            review.strengths = data.strengths
        if data.improvements:
            review.improvements = data.improvements
        review.status = "MANAGER_REVIEW"
        review.updated_at = datetime.now(UTC)
        return await self.perf_repo.update_review(review)

    async def submit_manager_review(
        self,
        review_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        data: PerformanceReviewManagerSubmit,
    ) -> PerformanceReview:
        review = await self.perf_repo.get_review(review_id, tenant_id, org_id)
        if not review:
            raise NotFoundException(f"Performance review '{review_id}' not found")

        review.manager_score = Decimal(str(data.manager_score))
        review.reviewer_id = user_id
        if data.strengths:
            review.strengths = f"{review.strengths or ''}\nManager: {data.strengths}".strip()
        if data.improvements:
            review.improvements = (
                f"{review.improvements or ''}\nManager: {data.improvements}".strip()
            )
        review.promotion_recommendation = data.promotion_recommendation
        if data.salary_revision_recommendation is not None:
            review.salary_revision_recommendation = Decimal(
                str(data.salary_revision_recommendation)
            )

        review.status = "HR_REVIEW"
        review.updated_at = datetime.now(UTC)
        return await self.perf_repo.update_review(review)

    async def finalize_review(
        self,
        review_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: PerformanceReviewFinalize,
    ) -> PerformanceReview:
        review = await self.perf_repo.get_review(review_id, tenant_id, org_id)
        if not review:
            raise NotFoundException(f"Performance review '{review_id}' not found")

        review.final_score = Decimal(str(data.final_score))
        review.final_rating = data.final_rating
        review.status = "FINALIZED"
        review.updated_at = datetime.now(UTC)
        return await self.perf_repo.update_review(review)

    async def get_review(
        self, review_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> PerformanceReview:
        review = await self.perf_repo.get_review(review_id, tenant_id, org_id)
        if not review:
            raise NotFoundException(f"Performance review '{review_id}' not found")
        return review

    async def list_reviews(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        employee_id: uuid.UUID | None = None,
        review_period_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> Sequence[PerformanceReview]:
        return await self.perf_repo.list_reviews(
            tenant_id, org_id, employee_id, review_period_id, status
        )
