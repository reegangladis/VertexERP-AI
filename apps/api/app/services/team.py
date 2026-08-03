import uuid

from fastapi import HTTPException, status

from app.models.team import Team, TeamMember
from app.repositories.team import TeamMemberRepository, TeamRepository
from app.schemas.team import TeamCreate, TeamMemberCreate, TeamUpdate
from app.services.base import BaseService


class TeamService(BaseService[Team, TeamRepository]):
    def __init__(self, repository: TeamRepository, member_repo: TeamMemberRepository):
        super().__init__(repository)
        self.member_repo = member_repo

    async def create_team(self, obj_in: TeamCreate) -> Team:
        if obj_in.code:
            existing = await self.repository.get_by_code(obj_in.organization_id, obj_in.code)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Team code '{obj_in.code}' already exists.",
                )
        created = await self.repository.create(obj_in.model_dump())
        return await self.repository.get_with_members(created.id) or created

    async def update_team(self, team_id: uuid.UUID, obj_in: TeamUpdate) -> Team:
        team = await self.repository.get(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Team not found."
            )
        if obj_in.code and obj_in.code != team.code:
            existing = await self.repository.get_by_code(team.organization_id, obj_in.code)
            if existing and existing.id != team_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Team code '{obj_in.code}' already exists.",
                )

        update_data = obj_in.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(team, k, v)
        await self.repository.db.commit()
        return await self.repository.get_with_members(team_id) or team

    async def add_member(self, team_id: uuid.UUID, obj_in: TeamMemberCreate) -> TeamMember:
        team = await self.repository.get(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Team not found."
            )
        existing = await self.member_repo.get_by_team_and_user(team_id, obj_in.user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this team.",
            )
        return await self.member_repo.create({"team_id": team_id, "user_id": obj_in.user_id, "role": obj_in.role})

    async def remove_member(self, team_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        member = await self.member_repo.get_by_team_and_user(team_id, user_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found."
            )
        await self.member_repo.delete(member.id)
        return True
