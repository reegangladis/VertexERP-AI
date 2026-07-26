import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# Deployment Schemas
class MLDeploymentCreate(BaseModel):
    model_id: uuid.UUID
    model_version_id: uuid.UUID
    name: str = Field(..., max_length=150)
    environment: str = Field(..., description="DEVELOPMENT, TESTING, STAGING, PRODUCTION")
    strategy: str = Field(default="BLUE_GREEN", description="BLUE_GREEN, CANARY, SHADOW")
    target_traffic_percentage: Optional[float] = 100.0
    config_json: Optional[Dict[str, Any]] = None


class MLDeploymentUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    strategy: Optional[str] = None
    target_traffic_percentage: Optional[float] = None
    active_version: Optional[str] = None
    endpoint_url: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None


class DeploymentTrafficUpdate(BaseModel):
    target_traffic_percentage: float = Field(..., ge=0.0, le=100.0)


class DeploymentRollbackRequest(BaseModel):
    target_version_id: uuid.UUID
    triggered_by: str = Field(..., max_length=150)
    notes: Optional[str] = None


class DeploymentHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    deployment_id: uuid.UUID
    previous_version_id: Optional[uuid.UUID]
    new_version_id: uuid.UUID
    action: str
    status: str
    triggered_by: str
    notes: Optional[str]
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
    endpoint_url: Optional[str]
    config_json: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    history: Optional[List[DeploymentHistoryResponse]] = None


# Pipeline Template Schemas
class PipelineTemplateCreate(BaseModel):
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    pipeline_type: str = Field(..., description="TRAINING, VALIDATION, DEPLOYMENT, PROMOTION, RETRAINING")
    version: str = Field(..., max_length=50)
    definition_json: Optional[Dict[str, Any]] = None


class PipelineTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: Optional[str]
    pipeline_type: str
    version: str
    definition_json: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Pipeline Run Schemas
class PipelineRunCreate(BaseModel):
    template_id: uuid.UUID
    model_id: Optional[uuid.UUID] = None
    model_version_id: Optional[uuid.UUID] = None
    run_name: str = Field(..., max_length=150)


class PipelineRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    template_id: uuid.UUID
    model_id: Optional[uuid.UUID]
    model_version_id: Optional[uuid.UUID]
    run_name: str
    status: str
    metrics_json: Optional[Dict[str, Any]]
    logs: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]


# Model Approval / Governance Schemas
class ModelApprovalCreate(BaseModel):
    model_version_id: uuid.UUID
    requested_by: str = Field(..., max_length=150)
    target_environment: str = Field(..., description="TESTING, STAGING, PRODUCTION")
    compliance_metadata_json: Optional[Dict[str, Any]] = None
    comments: Optional[str] = None


class ModelApprovalUpdate(BaseModel):
    approval_status: str = Field(..., description="APPROVED, REJECTED")
    approver: str = Field(..., max_length=150)
    comments: Optional[str] = None


class ModelApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    model_version_id: uuid.UUID
    request_date: datetime
    requested_by: str
    target_environment: str
    approval_status: str
    approver: Optional[str]
    decision_date: Optional[datetime]
    compliance_metadata_json: Optional[Dict[str, Any]]
    comments: Optional[str]
    created_at: datetime


# Model Monitoring Schemas
class ModelMonitoringMetricCreate(BaseModel):
    metric_name: str = Field(..., description="LATENCY, THROUGHPUT, ERROR_RATE, CPU_USAGE, MEMORY_USAGE")
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
    feature_name: Optional[str] = None
    drift_score: float
    status: str = Field(default="NORMAL", description="NORMAL, WARNING, CRITICAL")
    metrics_json: Optional[Dict[str, Any]] = None


class DriftReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    deployment_id: uuid.UUID
    drift_type: str
    feature_name: Optional[str]
    drift_score: float
    status: str
    metrics_json: Optional[Dict[str, Any]]
    created_at: datetime


# Retraining Job Schemas
class RetrainingJobCreate(BaseModel):
    model_id: uuid.UUID
    trigger_type: str = Field(..., description="MANUAL, SCHEDULED, DRIFT_TRIGGERED")
    config_json: Optional[Dict[str, Any]] = None


class RetrainingJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    model_id: uuid.UUID
    trigger_type: str
    status: str
    config_json: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
