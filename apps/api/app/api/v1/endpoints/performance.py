import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.performance import PerformanceReview, Goal
from app.repositories.hr_mgmt import PerformanceReviewRepository, GoalRepository
from app.schemas.hr_mgmt import (
    GoalResponse,
    GoalCreate,
    PerformanceReviewResponse,
    PerformanceReviewCreate,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

# 1. Goals & KPIs
@router.get("/goals", response_model=APIResponse[List[GoalResponse]])
async def list_goals(
    employee_id: Optional[uuid.UUID] = None,
    db=Depends(get_db_session)
):
    repo = GoalRepository(db)
    stmt = select(Goal).where(Goal.is_deleted == False)
    if employee_id:
        stmt = stmt.where(Goal.employee_id == employee_id)
    res = await db.execute(stmt)
    goals = list(res.scalars().all())
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Goals retrieved successfully",
        data=goals
    )

@router.post("/goals", response_model=APIResponse[GoalResponse])
async def create_goal(
    payload: GoalCreate,
    db=Depends(get_db_session)
):
    repo = GoalRepository(db)
    goal = await repo.create(payload.dict())
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Goal set successfully",
        data=goal
    )

# 2. Performance Reviews
@router.get("/reviews", response_model=APIResponse[List[PerformanceReviewResponse]])
async def list_reviews(
    employee_id: Optional[uuid.UUID] = None,
    db=Depends(get_db_session)
):
    repo = PerformanceReviewRepository(db)
    stmt = select(PerformanceReview).where(PerformanceReview.is_deleted == False)
    if employee_id:
        stmt = stmt.where(PerformanceReview.employee_id == employee_id)
    res = await db.execute(stmt)
    reviews = list(res.scalars().all())
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Performance reviews retrieved successfully",
        data=reviews
    )

@router.post("/reviews", response_model=APIResponse[PerformanceReviewResponse])
async def create_review(
    payload: PerformanceReviewCreate,
    db=Depends(get_db_session)
):
    repo = PerformanceReviewRepository(db)
    review = await repo.create(payload.dict())
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Performance review submitted",
        data=review
    )
