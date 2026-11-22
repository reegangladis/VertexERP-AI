"""Team and TeamMember schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TeamBase(BaseModel):
    """Base fields for team."""

    code: str = Field(..., min_length=1, max_length=32, description="Unique team code")
    name: str = Field(..., min_length=1, max_length=128, description="Team name")
    description: str | None = Field(None, description="Team description")
    department_id: uuid.UUID | None = Field(None, description="Department ID")
    lead_user_id: uuid.UUID | None = Field(None, description="Team Lead user ID")
    is_active: bool = True


class TeamCreate(TeamBase):
    """Schema for creating team."""

    pass


class TeamUpdate(BaseModel):
    """Schema for updating team."""

    code: str | None = Field(None, min_length=1, max_length=32)
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None
    department_id: uuid.UUID | None = None
    lead_user_id: uuid.UUID | None = None
    is_active: bool | None = None


class TeamResponse(TeamBase):
    """Response schema for team."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeamMemberAddRequest(BaseModel):
    """Request schema for adding a member to a team."""

    user_id: uuid.UUID = Field(..., description="User ID to add to team")
    role: str = Field(
        default="MEMBER", max_length=32, description="Team role e.g. LEAD, MEMBER, CONTRIBUTOR"
    )


class TeamMemberResponse(BaseModel):
    """Response schema for team member."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    team_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    joined_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
