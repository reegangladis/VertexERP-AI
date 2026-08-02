import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# =============================================================================
# METRICS SCHEMAS
# =============================================================================
class SystemMetricCreate(BaseModel):
    metric_name: str = Field(
        ..., description="Name of the metric (e.g. cpu_usage, api_latency)"
    )
    metric_type: str = Field(
        ..., description="Type of metric (gauge, counter, histogram)"
    )
    value: float = Field(..., description="Numerical value of the metric")
    labels: dict[str, Any] | None = Field(
        default=None, description="Metadata tags for metric labels"
    )


class SystemMetricResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    metric_name: str
    metric_type: str
    value: float
    labels: dict[str, Any] | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# LOG SCHEMAS
# =============================================================================
class ApplicationLogCreate(BaseModel):
    service_name: str = Field(..., description="Target microservice or module name")
    log_level: str = Field(..., description="Log level: INFO, WARNING, ERROR, DEBUG")
    message: str = Field(..., description="Actual log string details")
    structured_data: dict[str, Any] | None = Field(
        default=None, description="Additional context fields"
    )
    correlation_id: str | None = Field(
        default=None, description="ID for tracing transaction flows"
    )
    request_id: str | None = Field(default=None, description="HTTP Request ID context")


class ApplicationLogResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    service_name: str
    log_level: str
    message: str
    structured_data: dict[str, Any] | None = None
    correlation_id: str | None = None
    request_id: str | None = None
    timestamp: datetime

    class Config:
        from_attributes = True


# =============================================================================
# TRACING SCHEMAS
# =============================================================================
class TraceSpanCreate(BaseModel):
    trace_id: str = Field(..., description="Unified trace transaction ID")
    span_id: str = Field(..., description="Specific span execution ID")
    parent_span_id: str | None = Field(
        default=None, description="Parent span ID if nested"
    )
    name: str = Field(..., description="Operation details name")
    service_name: str = Field(..., description="Microservice triggering operation")
    start_time: datetime = Field(..., description="Start of execution")
    end_time: datetime = Field(..., description="End of execution")
    duration_ms: float = Field(..., description="Processing time in milliseconds")
    status: str = Field(..., description="Execution status (success, error)")
    attributes: dict[str, Any] | None = Field(
        default=None, description="Span parameters"
    )


class TraceSpanResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    name: str
    service_name: str
    start_time: datetime
    end_time: datetime
    duration_ms: float
    status: str
    attributes: dict[str, Any] | None = None

    class Config:
        from_attributes = True


class ServiceDependency(BaseModel):
    caller: str
    callee: str
    call_count: int
    avg_duration_ms: float
    error_rate: float


# =============================================================================
# ALERT SCHEMAS
# =============================================================================
class AlertCreate(BaseModel):
    rule_name: str = Field(..., description="Rule name triggering this alert")
    metric_name: str = Field(..., description="Target system metric checked")
    threshold: float = Field(..., description="Validation limit threshold")
    comparison_operator: str = Field(..., description="Operator (e.g. >, <, >=, <=)")
    current_value: float | None = None
    severity: str = Field(..., description="Severity level: critical, warning, info")
    description: str | None = None


class AlertUpdate(BaseModel):
    status: str | None = Field(
        default=None, description="State to change: acknowledged, resolved"
    )
    acknowledged_by: str | None = None
    description: str | None = None


class AlertHistoryResponse(BaseModel):
    id: uuid.UUID
    alert_id: uuid.UUID
    status_from: str
    status_to: str
    transition_reason: str | None = None
    changed_by: str | None = None
    timestamp: datetime

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    rule_name: str
    metric_name: str
    threshold: float
    comparison_operator: str
    current_value: float | None = None
    status: str
    severity: str
    description: str | None = None
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    created_at: datetime
    history: list[AlertHistoryResponse] = []

    class Config:
        from_attributes = True


# =============================================================================
# SERVICE HEALTH SCHEMAS
# =============================================================================
class ServiceHealthCreate(BaseModel):
    service_name: str
    status: str
    liveness: bool
    readiness: bool
    uptime_seconds: float
    latency_ms: float
    dependency_status: dict[str, str] | None = None


class ServiceHealthResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    service_name: str
    status: str
    liveness: bool
    readiness: bool
    uptime_seconds: float
    latency_ms: float
    dependency_status: dict[str, str] | None = None
    last_checked: datetime

    class Config:
        from_attributes = True


# =============================================================================
# DASHBOARD SCHEMAS
# =============================================================================
class DashboardConfigCreate(BaseModel):
    name: str = Field(..., description="Visual name for layout")
    dashboard_type: str = Field(
        ..., description="operations, api, infrastructure, business, ai, security"
    )
    config: dict[str, Any] = Field(
        default_factory=dict, description="Custom layout matrix parameters"
    )


class DashboardConfigUpdate(BaseModel):
    name: str | None = None
    config: dict[str, Any] | None = None


class DashboardConfigResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    name: str
    dashboard_type: str
    config: dict[str, Any]
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# OBSERVABILITY EVENTS SCHEMAS
# =============================================================================
class ObservabilityEventCreate(BaseModel):
    event_type: str
    name: str
    description: str | None = None
    severity: str
    event_metadata: dict[str, Any] | None = None


class ObservabilityEventResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    event_type: str
    name: str
    description: str | None = None
    severity: str
    event_metadata: dict[str, Any] | None = None
    timestamp: datetime

    class Config:
        from_attributes = True
