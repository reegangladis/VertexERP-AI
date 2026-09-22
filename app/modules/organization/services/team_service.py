"""Team and TeamMember service."""

import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.organization.models.team import Team, TeamMember
from app.modules.organization.repositories.team_repository import TeamRepository
from app.modules.organization.schemas.team import TeamCreate, TeamMemberAddRequest, TeamUpdate


class TeamService:
    """Business service for Team and TeamMember management."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.team_repo = TeamRepository(session)

    async def create_team(self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: TeamCreate) -> Team:
        existing = await self.team_repo.get_by_code(data.code, tenant_id, org_id)
        if existing:
            raise ConflictException(
                f"Team with code '{data.code}' already exists in this organization"
            )

        team = Team(
            tenant_id=tenant_id,
            organization_id=org_id,
            department_id=data.department_id,
            code=data.code,
            name=data.name,
            description=data.description,
            lead_user_id=data.lead_user_id,
            is_active=data.is_active,
        )
        return await self.team_repo.create(team)

    async def get_team(self, team_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID) -> Team:
        team = await self.team_repo.get_by_id(team_id, tenant_id, org_id)
        if not team:
            raise NotFoundException(f"Team '{team_id}' not found")
        return team

    async def list_teams(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[Team]:
        return await self.team_repo.list_by_org(tenant_id, org_id, is_active)

    async def update_team(
        self, team_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, data: TeamUpdate
    ) -> Team:
        team = await self.get_team(team_id, tenant_id, org_id)

        if data.code is not None and data.code != team.code:
            existing = await self.team_repo.get_by_code(data.code, tenant_id, org_id)
            if existing and existing.id != team.id:
                raise ConflictException(f"Team with code '{data.code}' already exists")
            team.code = data.code

        if data.name is not None:
            team.name = data.name
        if data.description is not None:
            team.description = data.description
        if data.department_id is not None:
            team.department_id = data.department_id
        if data.lead_user_id is not None:
            team.lead_user_id = data.lead_user_id
        if data.is_active is not None:
            team.is_active = data.is_active

        return await self.team_repo.update(team)

    async def delete_team(
        self, team_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> None:
        team = await self.get_team(team_id, tenant_id, org_id)
        await self.team_repo.soft_delete(team)

    # Team Members
    async def add_member(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        team_id: uuid.UUID,
        data: TeamMemberAddRequest,
    ) -> TeamMember:
        await self.get_team(team_id, tenant_id, org_id)
        existing = await self.team_repo.get_member(tenant_id, team_id, data.user_id)
        if existing:
            raise ConflictException("User is already a member of this team")

        member = TeamMember(
            tenant_id=tenant_id,
            team_id=team_id,
            user_id=data.user_id,
            role=data.role,
        )
        return await self.team_repo.add_member(member)

    async def list_members(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, team_id: uuid.UUID
    ) -> Sequence[TeamMember]:
        await self.get_team(team_id, tenant_id, org_id)
        return await self.team_repo.list_members(tenant_id, team_id)

    async def remove_member(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, team_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        await self.get_team(team_id, tenant_id, org_id)
        member = await self.team_repo.get_member(tenant_id, team_id, user_id)
        if not member:
            raise NotFoundException("Team member not found")
        await self.team_repo.remove_member(member)
