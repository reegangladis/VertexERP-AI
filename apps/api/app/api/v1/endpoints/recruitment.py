import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_current_user, get_db_session
from app.models.recruitment import Application, Interview
from app.models.user import User
from app.repositories.hr_mgmt import (
    ApplicationRepository,
    CandidateRepository,
    InterviewRepository,
    RecruitmentJobRepository,
)
from app.schemas.hr_mgmt import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
    CandidateCreate,
    CandidateResponse,
    InterviewCreate,
    InterviewResponse,
    RecruitmentJobCreate,
    RecruitmentJobResponse,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()


# 1. Job Positions Endpoints
@router.get("/jobs", response_model=APIResponse[list[RecruitmentJobResponse]])
async def list_jobs(
    current_user: User = Depends(get_current_user), db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = RecruitmentJobRepository(db)
    jobs = await repo.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Job positions retrieved successfully",
        data=jobs,
    )


@router.post("/jobs", response_model=APIResponse[RecruitmentJobResponse])
async def create_job(
    payload: RecruitmentJobCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = RecruitmentJobRepository(db)
    job = await repo.create(
        {"organization_id": current_user.organization_id, **payload.dict()}
    )
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Job position published successfully",
        data=job,
    )


# 2. Candidate Endpoints
@router.get("/candidates", response_model=APIResponse[list[CandidateResponse]])
async def list_candidates(
    current_user: User = Depends(get_current_user), db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = CandidateRepository(db)
    candidates = await repo.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Candidates retrieved successfully",
        data=candidates,
    )


@router.post("/candidates", response_model=APIResponse[CandidateResponse])
async def create_candidate(
    payload: CandidateCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = CandidateRepository(db)
    candidate = await repo.create(
        {"organization_id": current_user.organization_id, **payload.dict()}
    )
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Candidate created successfully",
        data=candidate,
    )


# 3. Application Pipeline Endpoints
@router.get("/applications", response_model=APIResponse[list[ApplicationResponse]])
async def list_applications(
    job_id: uuid.UUID | None = None, db=Depends(get_db_session)
):
    stmt = select(Application).where(Application.is_deleted == False)
    if job_id:
        stmt = stmt.where(Application.job_id == job_id)
    res = await db.execute(stmt)
    apps = list(res.scalars().all())
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Applications retrieved successfully",
        data=apps,
    )


@router.post("/applications", response_model=APIResponse[ApplicationResponse])
async def create_application(payload: ApplicationCreate, db=Depends(get_db_session)):
    repo = ApplicationRepository(db)
    app_obj = await repo.create(
        {**payload.dict(), "date_applied": datetime.now().date()}
    )
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Application submitted to hiring pipeline",
        data=app_obj,
    )


@router.put("/applications/{id}", response_model=APIResponse[ApplicationResponse])
async def update_application(
    id: uuid.UUID, payload: ApplicationUpdate, db=Depends(get_db_session)
):
    repo = ApplicationRepository(db)
    app_obj = await repo.get(id)
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    updated = await repo.update(app_obj, payload.dict(exclude_unset=True))
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Hiring stage updated",
        data=updated,
    )


# 4. Interview Scheduler Endpoints
@router.get("/interviews", response_model=APIResponse[list[InterviewResponse]])
async def list_interviews(
    application_id: uuid.UUID | None = None, db=Depends(get_db_session)
):
    stmt = select(Interview).where(Interview.is_deleted == False)
    if application_id:
        stmt = stmt.where(Interview.application_id == application_id)
    res = await db.execute(stmt)
    ints = list(res.scalars().all())
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Interviews retrieved successfully",
        data=ints,
    )


@router.post("/interviews", response_model=APIResponse[InterviewResponse])
async def create_interview(payload: InterviewCreate, db=Depends(get_db_session)):
    repo = InterviewRepository(db)
    int_obj = await repo.create(payload.dict())
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Interview scheduled successfully",
        data=int_obj,
    )
