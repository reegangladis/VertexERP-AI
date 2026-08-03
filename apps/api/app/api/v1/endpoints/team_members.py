import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_db_session
from app.models.user import User
from app.repositories.team import TeamMemberRepository, TeamRepository
from app.schemas.team import TeamMemberCreate, TeamMemberResponse
from app.services.team import TeamService

router = APIRouter()


def get_team_service(db: AsyncSession = Depends(get_db_session)) -> TeamService:
    return TeamService(TeamRepository(db), TeamMemberRepository(db))


@router.post("", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def create_team_member(
    data: TeamMemberCreate,
    current_user: User = Depends(PermissionChecker("team.manage")),
    service: TeamService = Depends(get_team_service),
):
    if not data.team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="team_id is required"
        )
    return await service.add_member(data.team_id, data)


@router.get("", response_model=list[TeamMemberResponse])
async def list_team_members(
    team_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(PermissionChecker("team.read")),
    service: TeamService = Depends(get_team_service),
):
    filters = {}
    if team_id:
        filters["team_id"] = team_id
    items, _ = await service.member_repo.get_multi(skip=skip, limit=limit, filters=filters)
    return items


@router.delete("/{id}")
async def delete_team_member(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("team.manage")),
    service: TeamService = Depends(get_team_service),
):
    member = await service.member_repo.get(id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found"
        )
    await service.member_repo.delete(id)
    return {"message": "Team member removed successfully"}
