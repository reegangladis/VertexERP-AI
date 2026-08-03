import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.team import Team, TeamMember
from app.repositories.base import BaseRepository


class TeamRepository(BaseRepository[Team]):
    def __init__(self, db: AsyncSession):
        super().__init__(Team, db)

    async def get_by_code(self, org_id: uuid.UUID, code: str) -> Team | None:
        stmt = (
            select(Team)
            .options(selectinload(Team.members))
            .where(
                Team.organization_id == org_id,
                Team.code == code,
                Team.is_deleted == False,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_members(self, team_id: uuid.UUID) -> Team | None:
        stmt = (
            select(Team)
            .options(selectinload(Team.members))
            .where(Team.id == team_id, Team.is_deleted == False)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class TeamMemberRepository(BaseRepository[TeamMember]):
    def __init__(self, db: AsyncSession):
        super().__init__(TeamMember, db)

    async def get_by_team_and_user(self, team_id: uuid.UUID, user_id: uuid.UUID) -> TeamMember | None:
        stmt = select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
            TeamMember.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
