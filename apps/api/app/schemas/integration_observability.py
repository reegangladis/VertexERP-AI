import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# --- API Key Schemas ---
class APIKeyBase(BaseModel):
    client_name: str = Field(..., min_length=1, max_length=255)
    permissions: str = Field(default="read,write", max_length=1000)
    status: str = Field(default="Active", max_length=50)


class APIKeyCreate(APIKeyBase):
    organization_id: uuid.UUID


class APIKeyResponse(APIKeyBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    api_key: str
    secret_key: str
    expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Webhook Schemas ---
class WebhookBase(BaseModel):
    event_name: str = Field(..., min_length=1, max_length=255)
    endpoint: str = Field(..., min_length=1, max_length=500)
    secret: str = Field(default="whsec_vertex_secret_key", max_length=255)
    status: str = Field(default="Active", max_length=50)


class WebhookCreate(WebhookBase):
    organization_id: uuid.UUID


class WebhookResponse(WebhookBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Notification Schemas ---
class NotificationBase(BaseModel):
    notification_type: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    channel: str = Field(default="Email", max_length=50)


class NotificationCreate(NotificationBase):
    organization_id: uuid.UUID
    user_id: uuid.UUID | None = None


class NotificationResponse(NotificationBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID | None = None
    status: str
    sent_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Observability Schemas ---
class ServiceHealthResponse(BaseModel):
    id: uuid.UUID
    service_name: str
    status: str
    latency: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    checked_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SystemMetricResponse(BaseModel):
    id: uuid.UUID
    metric_name: str
    metric_type: str
    metric_value: float
    instance: str
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Deployment & Backup Schemas ---
class DeploymentHistoryCreate(BaseModel):
    environment: str = Field(default="Production", max_length=50)
    version: str = Field(..., min_length=1, max_length=50)
    commit_hash: str = Field(..., min_length=1, max_length=100)
    deployed_by: str = Field(default="GitHub Actions", max_length=255)


class DeploymentHistoryResponse(BaseModel):
    id: uuid.UUID
    environment: str
    version: str
    commit_hash: str
    deployed_by: str
    started_at: datetime
    completed_at: datetime | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BackupJobCreate(BaseModel):
    backup_name: str = Field(..., min_length=1, max_length=255)
    storage_provider: str = Field(default="AWS S3", max_length=100)


class BackupJobResponse(BaseModel):
    id: uuid.UUID
    backup_name: str
    storage_provider: str
    backup_size: int
    started_at: datetime
    completed_at: datetime | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Security Audit Schemas ---
class SecurityAuditCreate(BaseModel):
    event: str = Field(..., min_length=1, max_length=255)
    severity: str = Field(default="INFO", max_length=50)
    details: str = Field(..., min_length=1)


class SecurityAuditResponse(BaseModel):
    id: uuid.UUID
    event: str
    severity: str
    details: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Ops Dashboard Summary Schema ---
class OpsDashboardSummary(BaseModel):
    active_api_keys: int
    active_webhooks: int
    notifications_sent: int
    overall_system_status: str
    avg_cpu_usage_pct: float
    avg_memory_usage_pct: float
    avg_latency_ms: float
    total_deployments: int
    total_backups_completed: int
    active_system_alerts: int
