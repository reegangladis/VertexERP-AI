"""Team and TeamMember API endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.modules.identity.models.user import User
from app.modules.organization.schemas.team import (
    TeamCreate,
    TeamMemberAddRequest,
    TeamMemberResponse,
    TeamResponse,
    TeamUpdate,
)
from app.modules.organization.services.team_service import TeamService

router = APIRouter(prefix="/teams", tags=["Team Management"])


@router.get(
    "/",
    response_model=list[TeamResponse],
    status_code=status.HTTP_200_OK,
    summary="List Teams",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_TEAMS_READ.value))],
)
async def list_teams(
    is_active: bool | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[TeamResponse]:
    """Lists all teams in active organization."""
    service = TeamService(db)
    teams = await service.list_teams(tenant_id, org_id, is_active)
    return [TeamResponse.model_validate(t) for t in teams]


@router.post(
    "/",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Team",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_TEAMS_WRITE.value))],
)
async def create_team(
    req: TeamCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TeamResponse:
    """Creates a team within the active organization."""
    service = TeamService(db)
    team = await service.create_team(tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="TEAM_CREATED",
        description=f"Team '{team.name}' ({team.code}) created by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return TeamResponse.model_validate(team)


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Team Details",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_TEAMS_READ.value))],
)
async def get_team(
    team_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> TeamResponse:
    """Retrieves team details enforcing tenant and org isolation."""
    service = TeamService(db)
    team = await service.get_team(team_id, tenant_id, org_id)
    return TeamResponse.model_validate(team)


@router.put(
    "/{team_id}",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Team",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_TEAMS_WRITE.value))],
)
async def update_team(
    team_id: uuid.UUID,
    req: TeamUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TeamResponse:
    """Updates team properties."""
    service = TeamService(db)
    team = await service.update_team(team_id, tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="TEAM_UPDATED",
        description=f"Team '{team.name}' updated by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return TeamResponse.model_validate(team)


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Team",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_TEAMS_WRITE.value))],
)
async def delete_team(
    team_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft deletes a team."""
    service = TeamService(db)
    await service.delete_team(team_id, tenant_id, org_id)

    await AuditService.log_security_event(
        session=db,
        event_type="TEAM_DELETED",
        description=f"Team '{team_id}' deleted by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )


# Member endpoints
@router.get(
    "/{team_id}/members",
    response_model=list[TeamMemberResponse],
    status_code=status.HTTP_200_OK,
    summary="List Team Members",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_TEAMS_READ.value))],
)
async def list_team_members(
    team_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[TeamMemberResponse]:
    """Lists roster members for a team."""
    service = TeamService(db)
    members = await service.list_members(tenant_id, org_id, team_id)
    return [TeamMemberResponse.model_validate(m) for m in members]


@router.post(
    "/{team_id}/members",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Member to Team",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_TEAMS_WRITE.value))],
)
async def add_team_member(
    team_id: uuid.UUID,
    req: TeamMemberAddRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TeamMemberResponse:
    """Adds a user to a team."""
    service = TeamService(db)
    member = await service.add_member(tenant_id, org_id, team_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="TEAM_MEMBER_ADDED",
        description=f"User '{req.user_id}' added to team '{team_id}' by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return TeamMemberResponse.model_validate(member)


@router.delete(
    "/{team_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove Member from Team",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_TEAMS_WRITE.value))],
)
async def remove_team_member(
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Removes a user from a team."""
    service = TeamService(db)
    await service.remove_member(tenant_id, org_id, team_id, user_id)

    await AuditService.log_security_event(
        session=db,
        event_type="TEAM_MEMBER_REMOVED",
        description=f"User '{user_id}' removed from team '{team_id}' by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )
