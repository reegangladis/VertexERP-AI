"""Recruitment service."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.hr.models.recruitment import (
    InterviewFeedback,
    InterviewSchedule,
    JobApplicant,
    JobOffer,
    JobRequisition,
)
from app.modules.hr.repositories.recruitment_repository import RecruitmentRepository
from app.modules.hr.schemas.recruitment import (
    InterviewFeedbackCreate,
    InterviewScheduleCreate,
    JobApplicantCreate,
    JobApplicantStageUpdate,
    JobOfferCreate,
    JobOfferStatusUpdate,
    JobRequisitionCreate,
    JobRequisitionUpdate,
)


class RecruitmentService:
    """Business service for Job Requisitions, Applicants, Interviews, and Offers."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.rec_repo = RecruitmentRepository(session)

    # --------------------------------------------------------------------------
    # Job Requisitions
    # --------------------------------------------------------------------------
    async def create_requisition(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: JobRequisitionCreate
    ) -> JobRequisition:
        req_num = await self.rec_repo.get_next_requisition_number(tenant_id, org_id)
        req = JobRequisition(
            tenant_id=tenant_id,
            organization_id=org_id,
            requisition_number=req_num,
            title=data.title,
            department_id=data.department_id,
            designation_id=data.designation_id,
            headcount=data.headcount,
            employment_type=data.employment_type,
            experience_level=data.experience_level,
            salary_min=Decimal(str(data.salary_min)),
            salary_max=Decimal(str(data.salary_max)),
            status="OPEN",
            target_hire_date=data.target_hire_date,
            description=data.description,
        )
        return await self.rec_repo.create_requisition(req)

    async def update_requisition(
        self, req_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, data: JobRequisitionUpdate
    ) -> JobRequisition:
        req = await self.rec_repo.get_requisition(req_id, tenant_id, org_id)
        if not req:
            raise NotFoundException(f"Job requisition '{req_id}' not found")

        if data.title is not None:
            req.title = data.title
        if data.headcount is not None:
            req.headcount = data.headcount
        if data.employment_type is not None:
            req.employment_type = data.employment_type
        if data.experience_level is not None:
            req.experience_level = data.experience_level
        if data.salary_min is not None:
            req.salary_min = Decimal(str(data.salary_min))
        if data.salary_max is not None:
            req.salary_max = Decimal(str(data.salary_max))
        if data.status is not None:
            req.status = data.status
        if data.target_hire_date is not None:
            req.target_hire_date = data.target_hire_date
        if data.description is not None:
            req.description = data.description

        req.updated_at = datetime.now(UTC)
        return await self.rec_repo.update_requisition(req)

    async def get_requisition(
        self, req_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> JobRequisition:
        req = await self.rec_repo.get_requisition(req_id, tenant_id, org_id)
        if not req:
            raise NotFoundException(f"Job requisition '{req_id}' not found")
        return req

    async def list_requisitions(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, status: str | None = None
    ) -> Sequence[JobRequisition]:
        return await self.rec_repo.list_requisitions(tenant_id, org_id, status)

    # --------------------------------------------------------------------------
    # Job Applicants
    # --------------------------------------------------------------------------
    async def create_applicant(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: JobApplicantCreate
    ) -> JobApplicant:
        req = await self.rec_repo.get_requisition(data.requisition_id, tenant_id, org_id)
        if not req:
            raise NotFoundException(f"Job requisition '{data.requisition_id}' not found")

        applicant = JobApplicant(
            tenant_id=tenant_id,
            organization_id=org_id,
            requisition_id=data.requisition_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            resume_url=data.resume_url,
            current_stage="APPLIED",
            rating=0,
            source=data.source,
        )
        return await self.rec_repo.create_applicant(applicant)

    async def update_applicant_stage(
        self,
        applicant_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: JobApplicantStageUpdate,
    ) -> JobApplicant:
        applicant = await self.rec_repo.get_applicant(applicant_id, tenant_id, org_id)
        if not applicant:
            raise NotFoundException(f"Job applicant '{applicant_id}' not found")

        applicant.current_stage = data.current_stage
        applicant.rating = data.rating
        return await self.rec_repo.update_applicant(applicant)

    async def get_applicant(
        self, applicant_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> JobApplicant:
        applicant = await self.rec_repo.get_applicant(applicant_id, tenant_id, org_id)
        if not applicant:
            raise NotFoundException(f"Job applicant '{applicant_id}' not found")
        return applicant

    async def list_applicants(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        requisition_id: uuid.UUID | None = None,
        current_stage: str | None = None,
    ) -> Sequence[JobApplicant]:
        return await self.rec_repo.list_applicants(tenant_id, org_id, requisition_id, current_stage)

    # --------------------------------------------------------------------------
    # Interviews & Feedbacks
    # --------------------------------------------------------------------------
    async def schedule_interview(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: InterviewScheduleCreate
    ) -> InterviewSchedule:
        applicant = await self.rec_repo.get_applicant(data.applicant_id, tenant_id, org_id)
        if not applicant:
            raise NotFoundException(f"Applicant '{data.applicant_id}' not found")

        interview = InterviewSchedule(
            tenant_id=tenant_id,
            organization_id=org_id,
            applicant_id=data.applicant_id,
            interviewer_id=data.interviewer_id,
            interview_type=data.interview_type,
            scheduled_at=data.scheduled_at,
            duration_minutes=data.duration_minutes,
            meeting_link=data.meeting_link,
            status="SCHEDULED",
        )
        applicant.current_stage = "INTERVIEW"
        await self.rec_repo.update_applicant(applicant)
        return await self.rec_repo.create_interview(interview)

    async def list_interviews_for_applicant(
        self, applicant_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[InterviewSchedule]:
        return await self.rec_repo.list_interviews_for_applicant(applicant_id, tenant_id, org_id)

    async def submit_feedback(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        data: InterviewFeedbackCreate,
    ) -> InterviewFeedback:
        interview = await self.rec_repo.get_interview(data.interview_id, tenant_id, org_id)
        if not interview:
            raise NotFoundException(f"Interview schedule '{data.interview_id}' not found")

        feedback = InterviewFeedback(
            tenant_id=tenant_id,
            organization_id=org_id,
            interview_id=data.interview_id,
            interviewer_id=user_id,
            rating=data.rating,
            score=Decimal(str(data.score)),
            strengths=data.strengths,
            weaknesses=data.weaknesses,
            recommendation=data.recommendation,
            notes=data.notes,
        )
        interview.status = "COMPLETED"
        await self.session.commit()
        return await self.rec_repo.create_feedback(feedback)

    async def list_feedbacks_for_interview(
        self, interview_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[InterviewFeedback]:
        return await self.rec_repo.list_feedbacks_for_interview(interview_id, tenant_id, org_id)

    # --------------------------------------------------------------------------
    # Job Offers
    # --------------------------------------------------------------------------
    async def create_offer(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: JobOfferCreate
    ) -> JobOffer:
        applicant = await self.rec_repo.get_applicant(data.applicant_id, tenant_id, org_id)
        if not applicant:
            raise NotFoundException(f"Applicant '{data.applicant_id}' not found")

        offer = JobOffer(
            tenant_id=tenant_id,
            organization_id=org_id,
            applicant_id=data.applicant_id,
            offered_designation_id=data.offered_designation_id,
            offered_salary=Decimal(str(data.offered_salary)),
            currency=data.currency,
            joining_date=data.joining_date,
            expiry_date=data.expiry_date,
            status="DRAFT",
        )
        applicant.current_stage = "OFFER"
        await self.rec_repo.update_applicant(applicant)
        return await self.rec_repo.create_offer(offer)

    async def update_offer_status(
        self,
        offer_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: JobOfferStatusUpdate,
    ) -> JobOffer:
        offer = await self.rec_repo.get_offer(offer_id, tenant_id, org_id)
        if not offer:
            raise NotFoundException(f"Job offer '{offer_id}' not found")

        offer.status = data.status
        if data.status == "ACCEPTED":
            applicant = await self.rec_repo.get_applicant(offer.applicant_id, tenant_id, org_id)
            if applicant:
                applicant.current_stage = "HIRED"
                await self.rec_repo.update_applicant(applicant)

        return await self.rec_repo.update_offer(offer)

    async def list_offers_for_applicant(
        self, applicant_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[JobOffer]:
        return await self.rec_repo.list_offers_for_applicant(applicant_id, tenant_id, org_id)
