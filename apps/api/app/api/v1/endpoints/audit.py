import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db_session, get_current_user, PermissionChecker
from app.schemas.audit import AuditLogResponse
from app.schemas.auth import LoginHistoryResponse
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response
from app.models.user import User

router = APIRouter()

# Services
async def get_audit_service(db: AsyncSession = Depends(get_db_session)):
    from app.repositories.audit import AuditLogRepository
    from app.services.audit import AuditService
    return AuditService(AuditLogRepository(db))

async def get_login_history_service(db: AsyncSession = Depends(get_db_session)):
    from app.repositories.audit import LoginHistoryRepository
    from app.services.audit import LoginHistoryService
    return LoginHistoryService(LoginHistoryRepository(db))

@router.get("/logs", response_model=APIResponse[list[AuditLogResponse]])
async def get_audit_logs(
    current_user: User = Depends(PermissionChecker("admin.full")),
    audit_service = Depends(get_audit_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not associated with an organization")
        
    logs = await audit_service.get_by_org(current_user.organization_id)
    data = [AuditLogResponse.model_validate(log) for log in logs]
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Audit logs retrieved",
        data=data
    )

@router.get("/login-history", response_model=APIResponse[list[LoginHistoryResponse]])
async def get_login_history(
    current_user: User = Depends(get_current_user),
    history_service = Depends(get_login_history_service)
):
    history = await history_service.get_by_user(current_user.id)
    data = [LoginHistoryResponse.model_validate(h) for h in history]
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Login history logs retrieved",
        data=data
    )
