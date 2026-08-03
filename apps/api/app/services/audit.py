import uuid

from app.models.audit_log import AuditLog
from app.repositories.audit import AuditLogRepository
from app.services.base import BaseService


class AuditLogService(BaseService[AuditLog, AuditLogRepository]):
    def __init__(self, repository: AuditLogRepository):
        super().__init__(repository)

    async def get_by_org(self, org_id: uuid.UUID) -> list[AuditLog]:
        return await self.repository.get_by_org_id(org_id)
