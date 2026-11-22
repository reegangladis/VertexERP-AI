"""Recruitment repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hr.models.recruitment import (
    InterviewFeedback,
    InterviewSchedule,
    JobApplicant,
    JobOffer,
    JobRequisition,
)


class RecruitmentRepository:
    """PostgreSQL implementation of Recruitment repository with multi-tenant filtering."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # --------------------------------------------------------------------------
    # Job Requisitions
    # --------------------------------------------------------------------------
    async def get_next_requisition_number(self, tenant_id: uuid.UUID, org_id: uuid.UUID) -> str:
        stmt = select(func.count(JobRequisition.id)).where(
            JobRequisition.tenant_id == tenant_id,
            JobRequisition.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        count = res.scalar() or 0
        return f"REQ-{count + 1:04d}"

    async def create_requisition(self, req: JobRequisition) -> JobRequisition:
        self.session.add(req)
        await self.session.commit()
        await self.session.refresh(req)
        return req

    async def get_requisition(
        self, req_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> JobRequisition | None:
        stmt = select(JobRequisition).where(
            JobRequisition.id == req_id,
            JobRequisition.tenant_id == tenant_id,
            JobRequisition.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_requisition(self, req: JobRequisition) -> JobRequisition:
        await self.session.commit()
        await self.session.refresh(req)
        return req

    async def list_requisitions(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, status: str | None = None
    ) -> Sequence[JobRequisition]:
        stmt = select(JobRequisition).where(
            JobRequisition.tenant_id == tenant_id,
            JobRequisition.organization_id == org_id,
        )
        if status:
            stmt = stmt.where(JobRequisition.status == status)
        stmt = stmt.order_by(JobRequisition.created_at.desc())
        res = await self.session.execute(stmt)
        return res.scalars().all()

    # --------------------------------------------------------------------------
    # Job Applicants
    # --------------------------------------------------------------------------
    async def create_applicant(self, applicant: JobApplicant) -> JobApplicant:
        self.session.add(applicant)
        await self.session.commit()
        await self.session.refresh(applicant)
        return applicant

    async def get_applicant(
        self, applicant_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> JobApplicant | None:
        stmt = select(JobApplicant).where(
            JobApplicant.id == applicant_id,
            JobApplicant.tenant_id == tenant_id,
            JobApplicant.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_applicant(self, applicant: JobApplicant) -> JobApplicant:
        await self.session.commit()
        await self.session.refresh(applicant)
        return applicant

    async def list_applicants(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        requisition_id: uuid.UUID | None = None,
        current_stage: str | None = None,
    ) -> Sequence[JobApplicant]:
        stmt = select(JobApplicant).where(
            JobApplicant.tenant_id == tenant_id,
            JobApplicant.organization_id == org_id,
        )
        if requisition_id:
            stmt = stmt.where(JobApplicant.requisition_id == requisition_id)
        if current_stage:
            stmt = stmt.where(JobApplicant.current_stage == current_stage)
        stmt = stmt.order_by(JobApplicant.created_at.desc())
        res = await self.session.execute(stmt)
        return res.scalars().all()

    # --------------------------------------------------------------------------
    # Interview Schedules & Feedback
    # --------------------------------------------------------------------------
    async def create_interview(self, interview: InterviewSchedule) -> InterviewSchedule:
        self.session.add(interview)
        await self.session.commit()
        await self.session.refresh(interview)
        return interview

    async def get_interview(
        self, interview_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> InterviewSchedule | None:
        stmt = select(InterviewSchedule).where(
            InterviewSchedule.id == interview_id,
            InterviewSchedule.tenant_id == tenant_id,
            InterviewSchedule.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_interviews_for_applicant(
        self, applicant_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[InterviewSchedule]:
        stmt = (
            select(InterviewSchedule)
            .where(
                InterviewSchedule.applicant_id == applicant_id,
                InterviewSchedule.tenant_id == tenant_id,
                InterviewSchedule.organization_id == org_id,
            )
            .order_by(InterviewSchedule.scheduled_at.asc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def create_feedback(self, feedback: InterviewFeedback) -> InterviewFeedback:
        self.session.add(feedback)
        await self.session.commit()
        await self.session.refresh(feedback)
        return feedback

    async def list_feedbacks_for_interview(
        self, interview_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[InterviewFeedback]:
        stmt = (
            select(InterviewFeedback)
            .where(
                InterviewFeedback.interview_id == interview_id,
                InterviewFeedback.tenant_id == tenant_id,
                InterviewFeedback.organization_id == org_id,
            )
            .order_by(InterviewFeedback.created_at.asc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    # --------------------------------------------------------------------------
    # Job Offers
    # --------------------------------------------------------------------------
    async def create_offer(self, offer: JobOffer) -> JobOffer:
        self.session.add(offer)
        await self.session.commit()
        await self.session.refresh(offer)
        return offer

    async def get_offer(
        self, offer_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> JobOffer | None:
        stmt = select(JobOffer).where(
            JobOffer.id == offer_id,
            JobOffer.tenant_id == tenant_id,
            JobOffer.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_offer(self, offer: JobOffer) -> JobOffer:
        await self.session.commit()
        await self.session.refresh(offer)
        return offer

    async def list_offers_for_applicant(
        self, applicant_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[JobOffer]:
        stmt = (
            select(JobOffer)
            .where(
                JobOffer.applicant_id == applicant_id,
                JobOffer.tenant_id == tenant_id,
                JobOffer.organization_id == org_id,
            )
            .order_by(JobOffer.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
