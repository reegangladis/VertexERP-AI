import uuid
from datetime import datetime
from pydantic import BaseModel

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None = None
    organization_id: uuid.UUID | None = None
    action: str
    ip_address: str
    user_agent: str
    details: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True
