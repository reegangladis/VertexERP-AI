"""CRM Pipeline and Pipeline Stages Pydantic Schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PipelineStageBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    stage_order: int = Field(default=0, ge=0)
    probability_pct: Decimal = Field(default=Decimal("10.00"), ge=0, le=100)
    stage_type: str = Field("OPEN", max_length=32)  # OPEN, WON, LOST
    is_active: bool = True


class PipelineStageCreate(PipelineStageBase):
    pipeline_id: uuid.UUID | None = None


class PipelineStageUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=64)
    stage_order: int | None = Field(None, ge=0)
    probability_pct: Decimal | None = Field(None, ge=0, le=100)
    stage_type: str | None = None
    is_active: bool | None = None


class PipelineStageResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    pipeline_id: uuid.UUID
    name: str
    stage_order: int
    probability_pct: Decimal
    stage_type: str
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PipelineBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    description: str | None = None
    is_default: bool = False
    is_active: bool = True


class PipelineCreate(PipelineBase):
    stages: list[PipelineStageBase] = Field(default_factory=list)


class PipelineUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=64)
    description: str | None = None
    is_default: bool | None = None
    is_active: bool | None = None


class PipelineResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None = None
    is_default: bool
    is_active: bool
    version: int
    stages: list[PipelineStageResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PipelineListResponse(BaseModel):
    items: list[PipelineResponse]
    total: int
    page: int
    page_size: int
