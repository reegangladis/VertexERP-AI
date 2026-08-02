import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# Deployment Schemas
class MLDeploymentCreate(BaseModel):
    model_id: uuid.UUID
    model_version_id: uuid.UUID
    name: str = Field(..., max_length=150)
    environment: str = Field(
        ..., description="DEVELOPMENT, TESTING, STAGING, PRODUCTION"
    )
    strategy: str = Field(
        default="BLUE_GREEN", description="BLUE_GREEN, CANARY, SHADOW"
    )
    target_traffic_percentage: float | None = 100.0
    config_json: dict[str, Any] | None = None


class MLDeploymentUpdate(BaseModel):
    name: str | None = None
    status: str | None = None
    strategy: str | None = None
    target_traffic_percentage: float | None = None
    active_version: str | None = None
    endpoint_url: str | None = None
    config_json: dict[str, Any] | None = None


class DeploymentTrafficUpdate(BaseModel):
    target_traffic_percentage: float = Field(..., ge=0.0, le=100.0)


class DeploymentRollbackRequest(BaseModel):
    target_version_id: uuid.UUID
    triggered_by: str = Field(..., max_length=150)
    notes: str | None = None


class DeploymentHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    deployment_id: uuid.UUID
    previous_version_id: uuid.UUID | None
    new_version_id: uuid.UUID
    action: str
    status: str
    triggered_by: str
    notes: str | None
    created_at: datetime


class MLDeploymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    model_id: uuid.UUID
    model_version_id: uuid.UUID
    name: str
    environment: str
    status: str
    strategy: str
    target_traffic_percentage: float
    active_version: str
    endpoint_url: str | None
    config_json: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
    history: list[DeploymentHistoryResponse] | None = None


# Pipeline Template Schemas
class PipelineTemplateCreate(BaseModel):
    name: str = Field(..., max_length=150)
    description: str | None = None
    pipeline_type: str = Field(
        ..., description="TRAINING, VALIDATION, DEPLOYMENT, PROMOTION, RETRAINING"
    )
    version: str = Field(..., max_length=50)
    definition_json: dict[str, Any] | None = None


class PipelineTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None
    pipeline_type: str
    version: str
    definition_json: dict[str, Any] | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Pipeline Run Schemas
class PipelineRunCreate(BaseModel):
    template_id: uuid.UUID
    model_id: uuid.UUID | None = None
    model_version_id: uuid.UUID | None = None
    run_name: str = Field(..., max_length=150)


class PipelineRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    template_id: uuid.UUID
    model_id: uuid.UUID | None
    model_version_id: uuid.UUID | None
    run_name: str
    status: str
    metrics_json: dict[str, Any] | None
    logs: str | None
    created_at: datetime
    completed_at: datetime | None


# Model Approval / Governance Schemas
class ModelApprovalCreate(BaseModel):
    model_version_id: uuid.UUID
    requested_by: str = Field(..., max_length=150)
    target_environment: str = Field(..., description="TESTING, STAGING, PRODUCTION")
    compliance_metadata_json: dict[str, Any] | None = None
    comments: str | None = None


class ModelApprovalUpdate(BaseModel):
    approval_status: str = Field(..., description="APPROVED, REJECTED")
    approver: str = Field(..., max_length=150)
    comments: str | None = None


class ModelApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    model_version_id: uuid.UUID
    request_date: datetime
    requested_by: str
    target_environment: str
    approval_status: str
    approver: str | None
    decision_date: datetime | None
    compliance_metadata_json: dict[str, Any] | None
    comments: str | None
    created_at: datetime


# Model Monitoring Schemas
class ModelMonitoringMetricCreate(BaseModel):
    metric_name: str = Field(
        ..., description="LATENCY, THROUGHPUT, ERROR_RATE, CPU_USAGE, MEMORY_USAGE"
    )
    metric_value: float


class ModelMonitoringMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    deployment_id: uuid.UUID
    metric_name: str
    metric_value: float
    timestamp: datetime


# Drift Report Schemas
class DriftReportCreate(BaseModel):
    drift_type: str = Field(..., description="DATA_DRIFT, PREDICTION_DRIFT")
    feature_name: str | None = None
    drift_score: float
    status: str = Field(default="NORMAL", description="NORMAL, WARNING, CRITICAL")
    metrics_json: dict[str, Any] | None = None


class DriftReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    deployment_id: uuid.UUID
    drift_type: str
    feature_name: str | None
    drift_score: float
    status: str
    metrics_json: dict[str, Any] | None
    created_at: datetime


# Retraining Job Schemas
class RetrainingJobCreate(BaseModel):
    model_id: uuid.UUID
    trigger_type: str = Field(..., description="MANUAL, SCHEDULED, DRIFT_TRIGGERED")
    config_json: dict[str, Any] | None = None


class RetrainingJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    model_id: uuid.UUID
    trigger_type: str
    status: str
    config_json: dict[str, Any] | None
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None
