import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ----------------------------------------------------
# Release Engineering Schemas
# ----------------------------------------------------
class ReleaseCreate(BaseModel):
    version: str = Field(..., description="SemVer string e.g. 'v1.0.0'")
    release_name: str = Field(..., max_length=150)
    release_type: str = Field(default="MAJOR", description="MAJOR, MINOR, PATCH, HOTFIX")
    git_commit_sha: str
    release_notes: Optional[str] = None
    artifacts: Optional[Dict[str, Any]] = None


class ReleaseOut(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    version: str
    release_name: str
    release_type: str
    status: str
    git_commit_sha: str
    release_notes: Optional[str] = None
    artifacts: Optional[Dict[str, Any]] = None
    released_by: str
    released_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RollbackRequest(BaseModel):
    target_version: str = Field(..., description="Target version string e.g. 'v0.9.5'")
    environment_name: str = "Production"
    reason: str = "Performance regression detected"


# ----------------------------------------------------
# Cloud Deployment Schemas
# ----------------------------------------------------
class DeploymentTriggerRequest(BaseModel):
    environment_name: str
    version: str
    strategy: str = "CANARY"  # CANARY, BLUE_GREEN, ROLLING
    canary_traffic_percent: float = 10.0


class DeploymentOut(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    environment_name: str
    version: str
    strategy: str
    status: str
    canary_traffic_percent: float
    duration_seconds: float
    error_log: Optional[str] = None
    deployed_by: str
    deployed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CloudRegionOut(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    region_code: str
    region_name: str
    provider: str
    role: str
    status: str
    latency_ms: float
    is_failover_ready: bool

    model_config = ConfigDict(from_attributes=True)


class FailoverTriggerRequest(BaseModel):
    primary_region: str = "us-east-1"
    secondary_region: str = "eu-central-1"
    reason: str = "Regional cloud outage simulation"


# ----------------------------------------------------
# FinOps Cost Monitoring Schemas
# ----------------------------------------------------
class CostReportOut(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    month_year: str
    provider: str
    total_cost_usd: float
    monthly_budget_usd: float
    service_breakdown: Optional[Dict[str, float]] = None
    recommendations: Optional[List[str]] = None
    budget_utilized_percent: float
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------
# Incident Management Schemas
# ----------------------------------------------------
class IncidentCreate(BaseModel):
    title: str = Field(..., max_length=200)
    severity: str = Field(default="P2", description="P1, P2, P3, P4")
    affected_services: Optional[List[str]] = Field(default_factory=lambda: ["api_gateway"])
    root_cause: Optional[str] = None


class IncidentOut(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    incident_number: str
    title: str
    severity: str
    status: str
    affected_services: Optional[List[str]] = None
    mttr_minutes: float
    root_cause: Optional[str] = None
    runbook_executed: Optional[str] = None
    assigned_oncall: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------
# System Status Schema
# ----------------------------------------------------
class GlobalSystemStatusOut(BaseModel):
    overall_status: str = "ALL_SYSTEMS_OPERATIONAL"
    version: str = "v1.0.0"
    active_regions: int = 3
    api_gateway_health: str = "HEALTHY"
    database_cluster_health: str = "HEALTHY"
    redis_cluster_health: str = "HEALTHY"
    uptime_percentage: float = 99.99
    last_updated: datetime
