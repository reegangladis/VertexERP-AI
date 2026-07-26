import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.training import TrainingCourse, TrainingRecord
from app.repositories.hr_mgmt import TrainingCourseRepository, TrainingRecordRepository
from app.schemas.hr_mgmt import (
    TrainingCourseResponse,
    TrainingCourseCreate,
    TrainingRecordResponse,
    TrainingRecordCreate,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

# 1. Course Endpoints
@router.get("/courses", response_model=APIResponse[List[TrainingCourseResponse]])
async def list_courses(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = TrainingCourseRepository(db)
    courses = await repo.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Training courses retrieved successfully",
        data=courses
    )

@router.post("/courses", response_model=APIResponse[TrainingCourseResponse])
async def create_course(
    payload: TrainingCourseCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = TrainingCourseRepository(db)
    course = await repo.create({"organization_id": current_user.organization_id, **payload.dict()})
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Training course created successfully",
        data=course
    )

# 2. Progress Tracker Endpoints
@router.get("/records", response_model=APIResponse[List[TrainingRecordResponse]])
async def list_records(
    employee_id: Optional[uuid.UUID] = None,
    db=Depends(get_db_session)
):
    repo = TrainingRecordRepository(db)
    stmt = select(TrainingRecord).where(TrainingRecord.is_deleted == False)
    if employee_id:
        stmt = stmt.where(TrainingRecord.employee_id == employee_id)
    res = await db.execute(stmt)
    records = list(res.scalars().all())
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Training assignments retrieved successfully",
        data=records
    )

@router.post("/records", response_model=APIResponse[TrainingRecordResponse])
async def assign_course(
    payload: TrainingRecordCreate,
    db=Depends(get_db_session)
):
    repo = TrainingRecordRepository(db)
    record = await repo.create(payload.dict())
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Course assigned to employee",
        data=record
    )
