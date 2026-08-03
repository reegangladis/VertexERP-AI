import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.repositories.audit import AuditLogRepository
from app.schemas.audit_log import AuditLogCreate, AuditLogResponse
from app.services.audit import AuditLogService

router = APIRouter()


def get_audit_service(
    db: AsyncSession = Depends(get_db_session),
) -> AuditLogService:
    return AuditLogService(AuditLogRepository(db))


@router.get("", response_model=list[AuditLogResponse])
async def list_audit_logs(
    organization_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    service: AuditLogService = Depends(get_audit_service),
):
    if organization_id:
        return await service.get_by_org(organization_id)
    items, _ = await service.get_multi(skip=skip, limit=limit)
    return items


@router.post("", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
async def create_audit_log(
    data: AuditLogCreate,
    service: AuditLogService = Depends(get_audit_service),
):
    return await service.create(data)


@router.get("/{id}", response_model=AuditLogResponse)
async def get_audit_log(
    id: uuid.UUID,
    service: AuditLogService = Depends(get_audit_service),
):
    log = await service.get(id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found"
        )
    return log
