from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogBase(BaseModel):
    action: str
    entity: str
    entity_id: str | None = None
    changes: dict | None = None


class AuditLogCreate(AuditLogBase):
    organization_id: UUID | None = None


class AuditLogResponse(AuditLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID | None = None
    timestamp: datetime
    created_at: datetime
