import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_current_user, get_db_session
from app.models.user import User
from app.repositories.team import TeamMemberRepository, TeamRepository
from app.schemas.team import TeamCreate, TeamMemberCreate, TeamMemberResponse, TeamResponse, TeamUpdate
from app.services.team import TeamService

router = APIRouter()


def get_team_service(db: AsyncSession = Depends(get_db_session)) -> TeamService:
    return TeamService(TeamRepository(db), TeamMemberRepository(db))


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    data: TeamCreate,
    current_user: User = Depends(PermissionChecker("team.manage")),
    service: TeamService = Depends(get_team_service),
):
    return await service.create_team(data)


@router.get("", response_model=list[TeamResponse])
async def list_teams(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(PermissionChecker("team.read")),
    service: TeamService = Depends(get_team_service),
):
    items, _ = await service.get_multi(skip=skip, limit=limit)
    return items


@router.get("/{id}", response_model=TeamResponse)
async def get_team(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("team.read")),
    service: TeamService = Depends(get_team_service),
):
    team = await service.repository.get_with_members(id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    return team


@router.patch("/{id}", response_model=TeamResponse)
async def update_team(
    id: uuid.UUID,
    data: TeamUpdate,
    current_user: User = Depends(PermissionChecker("team.manage")),
    service: TeamService = Depends(get_team_service),
):
    return await service.update_team(id, data)


@router.delete("/{id}", response_model=TeamResponse)
async def delete_team(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("team.manage")),
    service: TeamService = Depends(get_team_service),
):
    team = await service.delete(id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    return team


@router.post("/{id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_team_member(
    id: uuid.UUID,
    data: TeamMemberCreate,
    current_user: User = Depends(PermissionChecker("team.manage")),
    service: TeamService = Depends(get_team_service),
):
    return await service.add_member(id, data)


@router.delete("/{id}/members/{user_id}")
async def remove_team_member(
    id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("team.manage")),
    service: TeamService = Depends(get_team_service),
):
    await service.remove_member(id, user_id)
    return {"message": "Team member removed successfully"}
