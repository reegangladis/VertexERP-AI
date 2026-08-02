import uuid

from app.models.audit_log import AuditLog
from app.models.login_history import LoginHistory
from app.repositories.audit import AuditLogRepository, LoginHistoryRepository
from app.services.base import BaseService


class AuditService(BaseService[AuditLog, AuditLogRepository]):
    def __init__(self, repository: AuditLogRepository):
        super().__init__(repository)

    async def log_action(
        self,
        user_id: uuid.UUID | None,
        organization_id: uuid.UUID | None,
        action: str,
        ip_address: str,
        user_agent: str,
        details: dict | None = None,
    ) -> AuditLog:
        audit_in = {
            "user_id": user_id,
            "organization_id": organization_id,
            "action": action,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "details": details,
        }
        return await self.repository.create(audit_in)


class LoginHistoryService(BaseService[LoginHistory, LoginHistoryRepository]):
    def __init__(self, repository: LoginHistoryRepository):
        super().__init__(repository)

    async def log_login(
        self,
        user_id: uuid.UUID | None,
        email: str,
        ip_address: str,
        user_agent: str,
        browser: str | None,
        os: str | None,
        status: str,
        failure_reason: str | None = None,
    ) -> LoginHistory:
        history_in = {
            "user_id": user_id,
            "email": email,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "browser": browser,
            "os": os,
            "status": status,
            "failure_reason": failure_reason,
        }
        return await self.repository.create(history_in)
