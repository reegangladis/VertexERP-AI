from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TeamMemberBase(BaseModel):
    user_id: UUID
    role: str = "member"
    status: str = "active"


class TeamMemberCreate(TeamMemberBase):
    team_id: UUID | None = None


class TeamMemberResponse(TeamMemberBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    team_id: UUID
    joined_at: datetime


class TeamBase(BaseModel):
    name: str
    code: str | None = None
    description: str | None = None
    team_type: str | None = "cross_functional"
    manager_uuid: UUID | None = None
    team_lead_uuid: UUID | None = None
    status: str = "active"


class TeamCreate(TeamBase):
    organization_id: UUID
    department_id: UUID | None = None
    business_unit_id: UUID | None = None


class TeamUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None
    team_type: str | None = None
    manager_uuid: UUID | None = None
    team_lead_uuid: UUID | None = None
    department_id: UUID | None = None
    business_unit_id: UUID | None = None
    status: str | None = None


class TeamResponse(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    department_id: UUID | None = None
    business_unit_id: UUID | None = None
    members: list[TeamMemberResponse] = []
    created_at: datetime
    updated_at: datetime
