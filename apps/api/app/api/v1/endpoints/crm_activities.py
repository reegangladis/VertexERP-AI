from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user, get_db_session
from app.models.user import User
from app.repositories.crm_mgmt import CRMTaskRepository, MeetingRepository
from app.schemas.crm_mgmt import (
    CRMTaskCreate,
    CRMTaskResponse,
    MeetingCreate,
    MeetingResponse,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()


# 1. Tasks Endpoints
@router.get("/tasks", response_model=APIResponse[list[CRMTaskResponse]])
async def list_tasks(
    current_user: User = Depends(get_current_user), db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = CRMTaskRepository(db)
    tasks = await repo.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Tasks retrieved successfully",
        data=tasks,
    )


@router.post("/tasks", response_model=APIResponse[CRMTaskResponse])
async def create_task(
    payload: CRMTaskCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = CRMTaskRepository(db)
    task = await repo.create(
        {"organization_id": current_user.organization_id, **payload.dict()}
    )
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="CRM Task created successfully",
        data=task,
    )


# 2. Meetings Endpoints
@router.get("/meetings", response_model=APIResponse[list[MeetingResponse]])
async def list_meetings(
    current_user: User = Depends(get_current_user), db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = MeetingRepository(db)
    meetings = await repo.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Meetings retrieved successfully",
        data=meetings,
    )


@router.post("/meetings", response_model=APIResponse[MeetingResponse])
async def create_meeting(
    payload: MeetingCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = MeetingRepository(db)
    meeting = await repo.create(
        {"organization_id": current_user.organization_id, **payload.dict()}
    )
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Meeting scheduled successfully",
        data=meeting,
    )
