"""Recruitment, Job Requisitions, Applicants, Interviews, and Offers API endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.audit.services.audit_service import AuditService
from app.modules.hr.schemas.recruitment import (
    InterviewFeedbackCreate,
    InterviewFeedbackResponse,
    InterviewScheduleCreate,
    InterviewScheduleResponse,
    JobApplicantCreate,
    JobApplicantResponse,
    JobApplicantStageUpdate,
    JobOfferCreate,
    JobOfferResponse,
    JobOfferStatusUpdate,
    JobRequisitionCreate,
    JobRequisitionResponse,
    JobRequisitionUpdate,
)
from app.modules.hr.services.recruitment_service import RecruitmentService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.modules.identity.models.user import User

router = APIRouter(prefix="/recruitment", tags=["HR Recruitment & ATS"])


# --------------------------------------------------------------------------
# Job Requisitions
# --------------------------------------------------------------------------
@router.post(
    "/requisitions",
    response_model=JobRequisitionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Job Requisition",
    dependencies=[Depends(require_permission(PermissionCode.HR_RECRUITMENT_WRITE.value))],
)
async def create_requisition(
    req: JobRequisitionCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobRequisitionResponse:
    """Creates a new job opening requisition."""
    service = RecruitmentService(db)
    requisition = await service.create_requisition(tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_REQUISITION_CREATED",
        description=f"Job Requisition '{requisition.requisition_number}' ({requisition.title}) created by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return JobRequisitionResponse.model_validate(requisition)


@router.put(
    "/requisitions/{req_id}",
    response_model=JobRequisitionResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Job Requisition",
    dependencies=[Depends(require_permission(PermissionCode.HR_RECRUITMENT_WRITE.value))],
)
async def update_requisition(
    req_id: uuid.UUID,
    req: JobRequisitionUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobRequisitionResponse:
    """Updates job requisition details or status."""
    service = RecruitmentService(db)
    updated = await service.update_requisition(req_id, tenant_id, org_id, req)
    return JobRequisitionResponse.model_validate(updated)


@router.get(
    "/requisitions/{req_id}",
    response_model=JobRequisitionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Job Requisition",
    dependencies=[Depends(require_permission(PermissionCode.HR_RECRUITMENT_READ.value))],
)
async def get_requisition(
    req_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> JobRequisitionResponse:
    """Gets job requisition by ID."""
    service = RecruitmentService(db)
    requisition = await service.get_requisition(req_id, tenant_id, org_id)
    return JobRequisitionResponse.model_validate(requisition)


@router.get(
    "/requisitions",
    response_model=list[JobRequisitionResponse],
    status_code=status.HTTP_200_OK,
    summary="List Job Requisitions",
    dependencies=[Depends(require_permission(PermissionCode.HR_RECRUITMENT_READ.value))],
)
async def list_requisitions(
    status: str | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[JobRequisitionResponse]:
    """Lists job requisitions."""
    service = RecruitmentService(db)
    requisitions = await service.list_requisitions(tenant_id, org_id, status)
    return [JobRequisitionResponse.model_validate(r) for r in requisitions]


# --------------------------------------------------------------------------
# Job Applicants
# --------------------------------------------------------------------------
@router.post(
    "/applicants",
    response_model=JobApplicantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Job Applicant",
    dependencies=[Depends(require_permission(PermissionCode.HR_RECRUITMENT_WRITE.value))],
)
async def create_applicant(
    req: JobApplicantCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobApplicantResponse:
    """Registers a candidate application."""
    service = RecruitmentService(db)
    applicant = await service.create_applicant(tenant_id, org_id, req)
    return JobApplicantResponse.model_validate(applicant)


@router.put(
    "/applicants/{applicant_id}/stage",
    response_model=JobApplicantResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Applicant Pipeline Stage",
    dependencies=[Depends(require_permission(PermissionCode.HR_RECRUITMENT_WRITE.value))],
)
async def update_applicant_stage(
    applicant_id: uuid.UUID,
    req: JobApplicantStageUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobApplicantResponse:
    """Updates candidate hiring pipeline stage and rating."""
    service = RecruitmentService(db)
    applicant = await service.update_applicant_stage(applicant_id, tenant_id, org_id, req)
    return JobApplicantResponse.model_validate(applicant)


@router.get(
    "/applicants/{applicant_id}",
    response_model=JobApplicantResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Job Applicant",
    dependencies=[Depends(require_permission(PermissionCode.HR_RECRUITMENT_READ.value))],
)
async def get_applicant(
    applicant_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> JobApplicantResponse:
    """Gets applicant details."""
    service = RecruitmentService(db)
    applicant = await service.get_applicant(applicant_id, tenant_id, org_id)
    return JobApplicantResponse.model_validate(applicant)


@router.get(
    "/applicants",
    response_model=list[JobApplicantResponse],
    status_code=status.HTTP_200_OK,
    summary="List Job Applicants",
    dependencies=[Depends(require_permission(PermissionCode.HR_RECRUITMENT_READ.value))],
)
async def list_applicants(
    requisition_id: uuid.UUID | None = None,
    current_stage: str | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[JobApplicantResponse]:
    """Lists applicants with optional filters."""
    service = RecruitmentService(db)
    applicants = await service.list_applicants(tenant_id, org_id, requisition_id, current_stage)
    return [JobApplicantResponse.model_validate(a) for a in applicants]


# --------------------------------------------------------------------------
# Interview Schedules & Feedback
# --------------------------------------------------------------------------
@router.post(
    "/interviews",
    response_model=InterviewScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Schedule Interview Round",
    dependencies=[Depends(require_permission(PermissionCode.HR_RECRUITMENT_WRITE.value))],
)
async def schedule_interview(
    req: InterviewScheduleCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewScheduleResponse:
    """Schedules an interview round."""
    service = RecruitmentService(db)
    interview = await service.schedule_interview(tenant_id, org_id, req)
    return InterviewScheduleResponse.model_validate(interview)


@router.get(
    "/interviews/applicant/{applicant_id}",
    response_model=list[InterviewScheduleResponse],
    status_code=status.HTTP_200_OK,
    summary="List Interviews for Applicant",
    dependencies=[Depends(require_permission(PermissionCode.HR_RECRUITMENT_READ.value))],
)
async def list_interviews_for_applicant(
    applicant_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[InterviewScheduleResponse]:
    """Lists all scheduled interviews for an applicant."""
    service = RecruitmentService(db)
    interviews = await service.list_interviews_for_applicant(applicant_id, tenant_id, org_id)
    return [InterviewScheduleResponse.model_validate(i) for i in interviews]


@router.post(
    "/feedbacks",
    response_model=InterviewFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Interview Feedback",
    dependencies=[Depends(require_permission(PermissionCode.HR_RECRUITMENT_WRITE.value))],
)
async def submit_interview_feedback(
    req: InterviewFeedbackCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewFeedbackResponse:
    """Submits interviewer feedback and score."""
    service = RecruitmentService(db)
    feedback = await service.submit_feedback(tenant_id, org_id, current_user.id, req)
    return InterviewFeedbackResponse.model_validate(feedback)


@router.get(
    "/feedbacks/interview/{interview_id}",
    response_model=list[InterviewFeedbackResponse],
    status_code=status.HTTP_200_OK,
    summary="List Feedback for Interview",
    dependencies=[Depends(require_permission(PermissionCode.HR_RECRUITMENT_READ.value))],
)
async def list_feedbacks_for_interview(
    interview_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[InterviewFeedbackResponse]:
    """Lists feedback evaluations for an interview."""
    service = RecruitmentService(db)
    feedbacks = await service.list_feedbacks_for_interview(interview_id, tenant_id, org_id)
    return [InterviewFeedbackResponse.model_validate(f) for f in feedbacks]


# --------------------------------------------------------------------------
# Job Offers
# --------------------------------------------------------------------------
@router.post(
    "/offers",
    response_model=JobOfferResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Formal Job Offer",
    dependencies=[Depends(require_permission(PermissionCode.HR_RECRUITMENT_WRITE.value))],
)
async def create_job_offer(
    req: JobOfferCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobOfferResponse:
    """Extends a formal job offer to a candidate."""
    service = RecruitmentService(db)
    offer = await service.create_offer(tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_JOB_OFFER_EXTENDED",
        description=f"Job offer extended to applicant '{offer.applicant_id}' with salary {offer.offered_salary} {offer.currency}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return JobOfferResponse.model_validate(offer)


@router.put(
    "/offers/{offer_id}/status",
    response_model=JobOfferResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Offer Status",
    dependencies=[Depends(require_permission(PermissionCode.HR_RECRUITMENT_WRITE.value))],
)
async def update_offer_status(
    offer_id: uuid.UUID,
    req: JobOfferStatusUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobOfferResponse:
    """Updates offer status (SENT, ACCEPTED, DECLINED)."""
    service = RecruitmentService(db)
    offer = await service.update_offer_status(offer_id, tenant_id, org_id, req)
    return JobOfferResponse.model_validate(offer)


@router.get(
    "/offers/applicant/{applicant_id}",
    response_model=list[JobOfferResponse],
    status_code=status.HTTP_200_OK,
    summary="List Offers for Applicant",
    dependencies=[Depends(require_permission(PermissionCode.HR_RECRUITMENT_READ.value))],
)
async def list_offers_for_applicant(
    applicant_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[JobOfferResponse]:
    """Lists offers extended to an applicant."""
    service = RecruitmentService(db)
    offers = await service.list_offers_for_applicant(applicant_id, tenant_id, org_id)
    return [JobOfferResponse.model_validate(o) for o in offers]
