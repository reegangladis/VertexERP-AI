"""Team and TeamMember repository."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organization.models.team import Team, TeamMember


class TeamRepository:
    """Repository for Team and TeamMember persistence with strict tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, team_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Team | None:
        stmt = select(Team).where(
            Team.id == team_id,
            Team.tenant_id == tenant_id,
            Team.organization_id == org_id,
            Team.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID) -> Team | None:
        stmt = select(Team).where(
            Team.code == code,
            Team.tenant_id == tenant_id,
            Team.organization_id == org_id,
            Team.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[Team]:
        stmt = select(Team).where(
            Team.tenant_id == tenant_id,
            Team.organization_id == org_id,
            Team.is_deleted.is_(False),
        )
        if is_active is not None:
            stmt = stmt.where(Team.is_active.is_(is_active))
        stmt = stmt.order_by(Team.name.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, team: Team) -> Team:
        self.session.add(team)
        await self.session.flush()
        return team

    async def update(self, team: Team) -> Team:
        team.updated_at = datetime.now(UTC)
        team.version += 1
        await self.session.flush()
        return team

    async def soft_delete(self, team: Team) -> None:
        team.is_deleted = True
        team.deleted_at = datetime.now(UTC)
        team.version += 1
        await self.session.flush()

    # Team Members
    async def get_member(
        self, tenant_id: uuid.UUID, team_id: uuid.UUID, user_id: uuid.UUID
    ) -> TeamMember | None:
        stmt = select(TeamMember).where(
            TeamMember.tenant_id == tenant_id,
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_members(self, tenant_id: uuid.UUID, team_id: uuid.UUID) -> Sequence[TeamMember]:
        stmt = (
            select(TeamMember)
            .where(
                TeamMember.tenant_id == tenant_id,
                TeamMember.team_id == team_id,
            )
            .order_by(TeamMember.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_member(self, member: TeamMember) -> TeamMember:
        self.session.add(member)
        await self.session.flush()
        return member

    async def remove_member(self, member: TeamMember) -> None:
        await self.session.delete(member)
        await self.session.flush()
