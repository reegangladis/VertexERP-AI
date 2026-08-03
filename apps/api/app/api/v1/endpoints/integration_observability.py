import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_db_session
from app.models.user import User
from app.repositories.integration_observability import (
    APIKeyRepository,
    BackupJobRepository,
    DeploymentHistoryRepository,
    NotificationRepository,
    WebhookRepository,
)
from app.schemas.integration_observability import (
    APIKeyCreate,
    APIKeyResponse,
    BackupJobCreate,
    BackupJobResponse,
    DeploymentHistoryCreate,
    DeploymentHistoryResponse,
    NotificationCreate,
    NotificationResponse,
    OpsDashboardSummary,
    WebhookCreate,
    WebhookResponse,
)
from app.services.integration_observability import (
    BackupService,
    DeploymentService,
    IntegrationWebhookEngine,
    NotificationEngine,
    OpsAnalyticsService,
)

router = APIRouter()


# --- API Keys ---
@router.post("/ops/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def generate_api_key(
    payload: APIKeyCreate,
    current_user: User = Depends(PermissionChecker("integration.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = IntegrationWebhookEngine(db)
    return await engine.generate_api_key(payload)


@router.get("/ops/api-keys", response_model=list[APIKeyResponse])
async def list_api_keys(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("integration.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = APIKeyRepository(db)
    return await repo.get_by_org(org_id)


# --- Webhooks ---
@router.post("/ops/webhooks", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def register_webhook(
    payload: WebhookCreate,
    current_user: User = Depends(PermissionChecker("integration.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = IntegrationWebhookEngine(db)
    return await engine.register_webhook(payload)


@router.get("/ops/webhooks", response_model=list[WebhookResponse])
async def list_webhooks(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("integration.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = WebhookRepository(db)
    return await repo.get_by_org(org_id)


# --- Notifications ---
@router.post("/ops/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def send_notification(
    payload: NotificationCreate,
    current_user: User = Depends(PermissionChecker("notification.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = NotificationEngine(db)
    return await engine.send_notification(payload)


@router.get("/ops/notifications", response_model=list[NotificationResponse])
async def list_notifications(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("notification.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = NotificationRepository(db)
    return await repo.get_by_org(org_id)


# --- Deployments ---
@router.post("/ops/deployments", response_model=DeploymentHistoryResponse, status_code=status.HTTP_201_CREATED)
async def trigger_deployment(
    payload: DeploymentHistoryCreate,
    current_user: User = Depends(PermissionChecker("deployment.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = DeploymentService(db)
    return await service.trigger_deployment(payload)


@router.get("/ops/deployments", response_model=list[DeploymentHistoryResponse])
async def list_deployments(
    current_user: User = Depends(PermissionChecker("deployment.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = DeploymentHistoryRepository(db)
    records, _ = await repo.get_multi()
    return records


# --- Backups ---
@router.post("/ops/backups", response_model=BackupJobResponse, status_code=status.HTTP_201_CREATED)
async def create_backup(
    payload: BackupJobCreate,
    current_user: User = Depends(PermissionChecker("backup.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = BackupService(db)
    return await service.create_backup(payload)


@router.get("/ops/backups", response_model=list[BackupJobResponse])
async def list_backups(
    current_user: User = Depends(PermissionChecker("backup.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = BackupJobRepository(db)
    records, _ = await repo.get_multi()
    return records


# --- Ops Dashboard ---
@router.get("/ops/dashboard", response_model=OpsDashboardSummary)
async def get_ops_dashboard(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("monitoring.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = OpsAnalyticsService(db)
    return await service.get_dashboard_summary(org_id)
