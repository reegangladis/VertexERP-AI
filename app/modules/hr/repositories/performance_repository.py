"""Performance repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hr.models.performance import (
    EmployeeGoal,
    PerformanceReview,
    PerformanceReviewPeriod,
)


class PerformanceRepository:
    """PostgreSQL implementation of Performance repository with multi-tenant filtering."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # --------------------------------------------------------------------------
    # Review Periods
    # --------------------------------------------------------------------------
    async def create_period(self, period: PerformanceReviewPeriod) -> PerformanceReviewPeriod:
        self.session.add(period)
        await self.session.commit()
        await self.session.refresh(period)
        return period

    async def get_period(
        self, period_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> PerformanceReviewPeriod | None:
        stmt = select(PerformanceReviewPeriod).where(
            PerformanceReviewPeriod.id == period_id,
            PerformanceReviewPeriod.tenant_id == tenant_id,
            PerformanceReviewPeriod.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_period_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> PerformanceReviewPeriod | None:
        stmt = select(PerformanceReviewPeriod).where(
            PerformanceReviewPeriod.code == code,
            PerformanceReviewPeriod.tenant_id == tenant_id,
            PerformanceReviewPeriod.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_periods(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, status: str | None = None
    ) -> Sequence[PerformanceReviewPeriod]:
        stmt = select(PerformanceReviewPeriod).where(
            PerformanceReviewPeriod.tenant_id == tenant_id,
            PerformanceReviewPeriod.organization_id == org_id,
        )
        if status:
            stmt = stmt.where(PerformanceReviewPeriod.status == status)
        stmt = stmt.order_by(PerformanceReviewPeriod.start_date.desc())
        res = await self.session.execute(stmt)
        return res.scalars().all()

    # --------------------------------------------------------------------------
    # Employee Goals
    # --------------------------------------------------------------------------
    async def create_goal(self, goal: EmployeeGoal) -> EmployeeGoal:
        self.session.add(goal)
        await self.session.commit()
        await self.session.refresh(goal)
        return goal

    async def get_goal(
        self, goal_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> EmployeeGoal | None:
        stmt = select(EmployeeGoal).where(
            EmployeeGoal.id == goal_id,
            EmployeeGoal.tenant_id == tenant_id,
            EmployeeGoal.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_goal(self, goal: EmployeeGoal) -> EmployeeGoal:
        await self.session.commit()
        await self.session.refresh(goal)
        return goal

    async def list_goals(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        employee_id: uuid.UUID | None = None,
        review_period_id: uuid.UUID | None = None,
    ) -> Sequence[EmployeeGoal]:
        stmt = select(EmployeeGoal).where(
            EmployeeGoal.tenant_id == tenant_id,
            EmployeeGoal.organization_id == org_id,
        )
        if employee_id:
            stmt = stmt.where(EmployeeGoal.employee_id == employee_id)
        if review_period_id:
            stmt = stmt.where(EmployeeGoal.review_period_id == review_period_id)
        stmt = stmt.order_by(EmployeeGoal.created_at.desc())
        res = await self.session.execute(stmt)
        return res.scalars().all()

    # --------------------------------------------------------------------------
    # Performance Reviews
    # --------------------------------------------------------------------------
    async def create_review(self, review: PerformanceReview) -> PerformanceReview:
        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(review)
        return review

    async def get_review(
        self, review_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> PerformanceReview | None:
        stmt = select(PerformanceReview).where(
            PerformanceReview.id == review_id,
            PerformanceReview.tenant_id == tenant_id,
            PerformanceReview.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_review(self, review: PerformanceReview) -> PerformanceReview:
        await self.session.commit()
        await self.session.refresh(review)
        return review

    async def list_reviews(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        employee_id: uuid.UUID | None = None,
        review_period_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> Sequence[PerformanceReview]:
        stmt = select(PerformanceReview).where(
            PerformanceReview.tenant_id == tenant_id,
            PerformanceReview.organization_id == org_id,
        )
        if employee_id:
            stmt = stmt.where(PerformanceReview.employee_id == employee_id)
        if review_period_id:
            stmt = stmt.where(PerformanceReview.review_period_id == review_period_id)
        if status:
            stmt = stmt.where(PerformanceReview.status == status)
        stmt = stmt.order_by(PerformanceReview.created_at.desc())
        res = await self.session.execute(stmt)
        return res.scalars().all()
