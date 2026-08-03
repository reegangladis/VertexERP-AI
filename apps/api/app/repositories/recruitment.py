import uuid
from typing import Sequence
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.recruitment_v8 import (
    Application,
    Candidate,
    CandidateDocument,
    InterviewFeedback,
    InterviewRound,
    JobOffer,
    OnboardingTask,
    RecruitmentAgency,
    RecruitmentJob,
    RecruitmentPipelineLog,
)


class RecruitmentJobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, job: RecruitmentJob) -> RecruitmentJob:
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get_by_id(self, job_id: uuid.UUID) -> RecruitmentJob | None:
        stmt = (
            select(RecruitmentJob)
            .options(selectinload(RecruitmentJob.applications))
            .where(and_(RecruitmentJob.id == job_id, RecruitmentJob.is_deleted == False))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_code(self, org_id: uuid.UUID, code: str) -> RecruitmentJob | None:
        stmt = select(RecruitmentJob).where(
            and_(
                RecruitmentJob.organization_id == org_id,
                RecruitmentJob.job_code == code,
                RecruitmentJob.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(self, org_id: uuid.UUID) -> Sequence[RecruitmentJob]:
        stmt = (
            select(RecruitmentJob)
            .options(selectinload(RecruitmentJob.applications))
            .where(and_(RecruitmentJob.organization_id == org_id, RecruitmentJob.is_deleted == False))
            .order_by(RecruitmentJob.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def list_open_jobs(self, org_id: uuid.UUID) -> Sequence[RecruitmentJob]:
        stmt = (
            select(RecruitmentJob)
            .where(
                and_(
                    RecruitmentJob.organization_id == org_id,
                    RecruitmentJob.status == "Open",
                    RecruitmentJob.is_deleted == False,
                )
            )
            .order_by(RecruitmentJob.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, job: RecruitmentJob) -> RecruitmentJob:
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def delete(self, job_id: uuid.UUID) -> RecruitmentJob | None:
        job = await self.get_by_id(job_id)
        if job:
            job.is_deleted = True
            await self.db.commit()
        return job


class CandidateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, candidate: Candidate) -> Candidate:
        self.db.add(candidate)
        await self.db.commit()
        await self.db.refresh(candidate)
        return candidate

    async def get_by_id(self, candidate_id: uuid.UUID) -> Candidate | None:
        stmt = (
            select(Candidate)
            .options(
                selectinload(Candidate.applications),
                selectinload(Candidate.documents),
            )
            .where(and_(Candidate.id == candidate_id, Candidate.is_deleted == False))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_email(self, org_id: uuid.UUID, email: str) -> Candidate | None:
        stmt = select(Candidate).where(
            and_(
                Candidate.organization_id == org_id,
                Candidate.email == email,
                Candidate.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(self, org_id: uuid.UUID) -> Sequence[Candidate]:
        stmt = (
            select(Candidate)
            .where(and_(Candidate.organization_id == org_id, Candidate.is_deleted == False))
            .order_by(Candidate.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, candidate: Candidate) -> Candidate:
        await self.db.commit()
        await self.db.refresh(candidate)
        return candidate

    async def delete(self, candidate_id: uuid.UUID) -> Candidate | None:
        cand = await self.get_by_id(candidate_id)
        if cand:
            cand.is_deleted = True
            await self.db.commit()
        return cand


class ApplicationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, application: Application) -> Application:
        self.db.add(application)
        await self.db.commit()
        await self.db.refresh(application)
        return application

    async def get_by_id(self, application_id: uuid.UUID) -> Application | None:
        stmt = (
            select(Application)
            .options(
                selectinload(Application.interview_rounds).selectinload(InterviewRound.feedback),
                selectinload(Application.offers),
                selectinload(Application.pipeline_logs),
            )
            .where(and_(Application.id == application_id, Application.is_deleted == False))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_candidate_and_job(
        self, candidate_id: uuid.UUID, job_id: uuid.UUID
    ) -> Application | None:
        stmt = select(Application).where(
            and_(
                Application.candidate_id == candidate_id,
                Application.job_id == job_id,
                Application.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_job(self, job_id: uuid.UUID) -> Sequence[Application]:
        stmt = (
            select(Application)
            .options(
                selectinload(Application.interview_rounds).selectinload(InterviewRound.feedback),
                selectinload(Application.offers),
            )
            .where(and_(Application.job_id == job_id, Application.is_deleted == False))
            .order_by(Application.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def list_by_candidate(self, candidate_id: uuid.UUID) -> Sequence[Application]:
        stmt = (
            select(Application)
            .where(and_(Application.candidate_id == candidate_id, Application.is_deleted == False))
            .order_by(Application.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, application: Application) -> Application:
        await self.db.commit()
        await self.db.refresh(application)
        return application


class InterviewRoundRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, round_obj: InterviewRound) -> InterviewRound:
        self.db.add(round_obj)
        await self.db.commit()
        await self.db.refresh(round_obj)
        return round_obj

    async def get_by_id(self, round_id: uuid.UUID) -> InterviewRound | None:
        stmt = (
            select(InterviewRound)
            .options(selectinload(InterviewRound.feedback))
            .where(and_(InterviewRound.id == round_id, InterviewRound.is_deleted == False))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_application(self, application_id: uuid.UUID) -> Sequence[InterviewRound]:
        stmt = (
            select(InterviewRound)
            .options(selectinload(InterviewRound.feedback))
            .where(and_(InterviewRound.application_id == application_id, InterviewRound.is_deleted == False))
            .order_by(InterviewRound.round_number.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, round_obj: InterviewRound) -> InterviewRound:
        await self.db.commit()
        await self.db.refresh(round_obj)
        return round_obj


class InterviewFeedbackRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, feedback: InterviewFeedback) -> InterviewFeedback:
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    async def list_by_round(self, round_id: uuid.UUID) -> Sequence[InterviewFeedback]:
        stmt = select(InterviewFeedback).where(
            and_(InterviewFeedback.interview_round_id == round_id, InterviewFeedback.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()


class JobOfferRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, offer: JobOffer) -> JobOffer:
        self.db.add(offer)
        await self.db.commit()
        await self.db.refresh(offer)
        return offer

    async def get_by_id(self, offer_id: uuid.UUID) -> JobOffer | None:
        stmt = (
            select(JobOffer)
            .options(selectinload(JobOffer.onboarding_tasks))
            .where(and_(JobOffer.id == offer_id, JobOffer.is_deleted == False))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_application(self, application_id: uuid.UUID) -> JobOffer | None:
        stmt = (
            select(JobOffer)
            .options(selectinload(JobOffer.onboarding_tasks))
            .where(and_(JobOffer.application_id == application_id, JobOffer.is_deleted == False))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def update(self, offer: JobOffer) -> JobOffer:
        await self.db.commit()
        await self.db.refresh(offer)
        return offer


class CandidateDocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, doc: CandidateDocument) -> CandidateDocument:
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def list_by_candidate(self, candidate_id: uuid.UUID) -> Sequence[CandidateDocument]:
        stmt = select(CandidateDocument).where(
            and_(CandidateDocument.candidate_id == candidate_id, CandidateDocument.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()


class OnboardingTaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, task: OnboardingTask) -> OnboardingTask:
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_by_id(self, task_id: uuid.UUID) -> OnboardingTask | None:
        stmt = select(OnboardingTask).where(
            and_(OnboardingTask.id == task_id, OnboardingTask.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_offer(self, offer_id: uuid.UUID) -> Sequence[OnboardingTask]:
        stmt = select(OnboardingTask).where(
            and_(OnboardingTask.offer_id == offer_id, OnboardingTask.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, task: OnboardingTask) -> OnboardingTask:
        await self.db.commit()
        await self.db.refresh(task)
        return task


class RecruitmentAgencyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, agency: RecruitmentAgency) -> RecruitmentAgency:
        self.db.add(agency)
        await self.db.commit()
        await self.db.refresh(agency)
        return agency

    async def list(self, org_id: uuid.UUID) -> Sequence[RecruitmentAgency]:
        stmt = select(RecruitmentAgency).where(
            and_(RecruitmentAgency.organization_id == org_id, RecruitmentAgency.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()


class RecruitmentPipelineLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, log: RecruitmentPipelineLog) -> RecruitmentPipelineLog:
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log


# Backward compatibility aliases
JobRequisitionRepository = RecruitmentJobRepository
InterviewRepository = InterviewRoundRepository
OfferRepository = JobOfferRepository
