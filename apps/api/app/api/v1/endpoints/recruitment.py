import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_db_session
from app.models.user import User
from app.schemas.recruitment import (
    ApplicationCreate,
    ApplicationMoveStage,
    ApplicationResponse,
    CandidateCreate,
    CandidateDocumentCreate,
    CandidateDocumentResponse,
    CandidateResponse,
    CandidateUpdate,
    InterviewFeedbackCreate,
    InterviewFeedbackResponse,
    InterviewRoundCreate,
    InterviewRoundResponse,
    InterviewRoundUpdate,
    JobOfferCreate,
    JobOfferResponse,
    JobOfferUpdate,
    OnboardingTaskResponse,
    OnboardingTaskUpdate,
    RecruitmentAgencyCreate,
    RecruitmentAgencyResponse,
    RecruitmentDashboardSummary,
    RecruitmentJobCreate,
    RecruitmentJobResponse,
    RecruitmentJobUpdate,
)
from app.services.recruitment import RecruitmentService

router = APIRouter()


def get_recruitment_service(db: AsyncSession = Depends(get_db_session)) -> RecruitmentService:
    return RecruitmentService(db)


# --- Recruitment Jobs ---
@router.post("/recruitment-jobs", response_model=RecruitmentJobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: RecruitmentJobCreate,
    current_user: User = Depends(PermissionChecker("recruitment.create")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.create_job(payload)


@router.get("/recruitment-jobs", response_model=list[RecruitmentJobResponse])
async def list_jobs(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("recruitment.read")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.list_jobs(org_id)


@router.get("/recruitment-jobs/{id}", response_model=RecruitmentJobResponse)
async def get_job(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("recruitment.read")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.get_job(id)


@router.patch("/recruitment-jobs/{id}", response_model=RecruitmentJobResponse)
async def update_job(
    id: uuid.UUID,
    payload: RecruitmentJobUpdate,
    current_user: User = Depends(PermissionChecker("recruitment.update")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.update_job(id, payload)


@router.delete("/recruitment-jobs/{id}", response_model=RecruitmentJobResponse)
async def delete_job(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("recruitment.delete")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.delete_job(id)


# --- Candidates ---
@router.post("/candidates", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    payload: CandidateCreate,
    current_user: User = Depends(PermissionChecker("candidate.manage")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.create_candidate(payload)


@router.get("/candidates", response_model=list[CandidateResponse])
async def list_candidates(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("recruitment.read")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.list_candidates(org_id)


@router.get("/candidates/{id}", response_model=CandidateResponse)
async def get_candidate(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("recruitment.read")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.get_candidate(id)


@router.patch("/candidates/{id}", response_model=CandidateResponse)
async def update_candidate(
    id: uuid.UUID,
    payload: CandidateUpdate,
    current_user: User = Depends(PermissionChecker("candidate.manage")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.update_candidate(id, payload)


@router.delete("/candidates/{id}", response_model=CandidateResponse)
async def delete_candidate(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("candidate.manage")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.delete_candidate(id)


# --- Job Applications ---
@router.post("/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_for_job(
    payload: ApplicationCreate,
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.apply_for_job(payload)


@router.get("/applications", response_model=list[ApplicationResponse])
async def list_applications_by_job(
    job_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("recruitment.read")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.list_applications_by_job(job_id)


@router.post("/applications/{id}/move-stage", response_model=ApplicationResponse)
async def move_pipeline_stage(
    id: uuid.UUID,
    payload: ApplicationMoveStage,
    current_user: User = Depends(PermissionChecker("candidate.manage")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.move_pipeline_stage(id, payload)


@router.post("/applications/{id}/withdraw", response_model=ApplicationResponse)
async def withdraw_application(
    id: uuid.UUID,
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.withdraw_application(id)


# --- Interview Rounds & Feedback ---
@router.post("/interview-rounds", response_model=InterviewRoundResponse, status_code=status.HTTP_201_CREATED)
async def schedule_interview(
    payload: InterviewRoundCreate,
    current_user: User = Depends(PermissionChecker("interview.manage")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.schedule_interview(payload)


@router.post("/interview-feedback", response_model=InterviewFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    payload: InterviewFeedbackCreate,
    current_user: User = Depends(PermissionChecker("interview.manage")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.submit_feedback(payload)


# --- Job Offers ---
@router.post("/job-offers", response_model=JobOfferResponse, status_code=status.HTTP_201_CREATED)
async def create_offer(
    payload: JobOfferCreate,
    current_user: User = Depends(PermissionChecker("offer.manage")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.create_offer(payload)


@router.post("/job-offers/{id}/accept", response_model=JobOfferResponse)
async def accept_offer(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("offer.manage")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.accept_offer(id)


@router.post("/job-offers/{id}/reject", response_model=JobOfferResponse)
async def reject_offer(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("offer.manage")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.reject_offer(id)


# --- Candidate Documents ---
@router.post("/candidate-documents", response_model=CandidateDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    payload: CandidateDocumentCreate,
    current_user: User = Depends(PermissionChecker("candidate.manage")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.upload_document(payload)


@router.post("/candidate-documents/{id}/verify", response_model=CandidateDocumentResponse)
async def verify_document(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("candidate.manage")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.verify_document(id)


# --- Onboarding Tasks ---
@router.get("/onboarding-tasks", response_model=list[OnboardingTaskResponse])
async def list_onboarding_tasks(
    offer_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("onboarding.manage")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.list_onboarding_tasks(offer_id)


@router.patch("/onboarding-tasks/{id}", response_model=OnboardingTaskResponse)
async def update_onboarding_task(
    id: uuid.UUID,
    payload: OnboardingTaskUpdate,
    current_user: User = Depends(PermissionChecker("onboarding.manage")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.update_onboarding_task(id, payload)


# --- Recruitment Agencies ---
@router.post("/recruitment-agencies", response_model=RecruitmentAgencyResponse, status_code=status.HTTP_201_CREATED)
async def create_agency(
    payload: RecruitmentAgencyCreate,
    current_user: User = Depends(PermissionChecker("recruitment.create")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.create_agency(payload)


@router.get("/recruitment-agencies", response_model=list[RecruitmentAgencyResponse])
async def list_agencies(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("recruitment.read")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.list_agencies(org_id)


# --- Dashboard Summary ---
@router.get("/recruitment-dashboard-summary", response_model=RecruitmentDashboardSummary)
async def get_dashboard_summary(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("recruitment.read")),
    service: RecruitmentService = Depends(get_recruitment_service),
):
    return await service.get_dashboard_summary(org_id)
