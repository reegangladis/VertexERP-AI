import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import RoleChecker, get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.observability import (
    AlertCreate,
    AlertResponse,
    AlertUpdate,
    ApplicationLogCreate,
    ApplicationLogResponse,
    DashboardConfigCreate,
    DashboardConfigResponse,
    ObservabilityEventResponse,
    ServiceDependency,
    SystemMetricCreate,
    SystemMetricResponse,
    TraceSpanCreate,
    TraceSpanResponse,
)
from app.schemas.response import APIResponse
from app.services.observability_service import ObservabilityService

router = APIRouter()

# Restrict monitoring write and dashboard updates to specific platform-engineering roles
platform_role_checker = RoleChecker(
    ["Super Admin", "SRE", "Platform Admin", "DevOps", "Organization Admin", "Admin"]
)
read_role_checker = RoleChecker(
    ["Super Admin", "SRE", "Platform Admin", "DevOps", "Developer", "Admin", "Organization Admin"]
)


# =============================================================================
# HEALTH CHECKS
# =============================================================================
@router.get("/health", response_model=APIResponse[dict])
async def get_observability_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Detailed health check for all ERP services, REST APIs, databases, authentication, Celery, and AI endpoints."""
    service = ObservabilityService(db)
    # Standard tenant constraint
    health_data = await service.get_system_health(current_user.organization_id)
    return APIResponse(
        success=True,
        message="System dependency states fetched successfully",
        data=health_data,
    )


# =============================================================================
# METRICS ENDPOINTS
# =============================================================================
@router.post(
    "/metrics",
    response_model=APIResponse[SystemMetricResponse],
    status_code=status.HTTP_201_CREATED,
)
async def record_system_metric(
    payload: SystemMetricCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _role=Depends(platform_role_checker),
):
    """Submits system telemetry metrics (CPU, Memory, API latency, database performance, RAG retrieval)."""
    service = ObservabilityService(db)
    metric = await service.record_metric(current_user.organization_id, payload)
    return APIResponse(
        success=True,
        message="System metric recorded successfully",
        data=SystemMetricResponse.model_validate(metric),
    )


@router.get("/metrics", response_model=APIResponse[list[SystemMetricResponse]])
async def query_system_metrics(
    metric_name: str | None = Query(None, description="Filter metrics by name"),
    duration_minutes: int = Query(60, description="Duration in minutes to look back"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _role=Depends(read_role_checker),
):
    """Queries time-series system performance metrics under tenant isolation constraints."""
    service = ObservabilityService(db)
    metrics = await service.get_system_metrics(
        current_user.organization_id, metric_name, duration_minutes
    )
    return APIResponse(
        success=True,
        message="System metrics fetched successfully",
        data=[SystemMetricResponse.model_validate(m) for m in metrics],
    )


@router.get("/business", response_model=APIResponse[dict])
async def query_business_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _role=Depends(read_role_checker),
):
    """Retrieves business intelligence metrics (orders, revenues, inventory levels, HR turnover)."""
    service = ObservabilityService(db)
    metrics = await service.get_business_observability(current_user.organization_id)
    return APIResponse(
        success=True,
        message="Business observability metrics fetched successfully",
        data=metrics,
    )


@router.get("/ai", response_model=APIResponse[dict])
async def query_ai_observability_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _role=Depends(read_role_checker),
):
    """Retrieves AI observability metrics (LLM execution latency, prompt tokens, vector recall)."""
    service = ObservabilityService(db)
    metrics = await service.get_ai_observability(current_user.organization_id)
    return APIResponse(
        success=True,
        message="AI observability metrics fetched successfully",
        data=metrics,
    )


# =============================================================================
# LOGS ENDPOINTS
# =============================================================================
@router.post(
    "/logs",
    response_model=APIResponse[ApplicationLogResponse],
    status_code=status.HTTP_201_CREATED,
)
async def submit_application_log(
    payload: ApplicationLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _role=Depends(platform_role_checker),
):
    """Submits a structured application execution log."""
    service = ObservabilityService(db)
    log = await service.write_log(current_user.organization_id, payload)
    return APIResponse(
        success=True,
        message="Application log written successfully",
        data=ApplicationLogResponse.model_validate(log),
    )


@router.get("/logs", response_model=APIResponse[dict])
async def query_application_logs(
    service_name: str | None = Query(None),
    log_level: str | None = Query(None),
    keyword: str | None = Query(None),
    correlation_id: str | None = Query(None),
    request_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _role=Depends(read_role_checker),
):
    """Searches structured application logs utilizing full-text keyword matching and correlation IDs."""
    service = ObservabilityService(db)
    logs, total = await service.search_logs(
        organization_id=current_user.organization_id,
        service_name=service_name,
        log_level=log_level,
        keyword=keyword,
        correlation_id=correlation_id,
        request_id=request_id,
        page=page,
        page_size=page_size,
    )
    return APIResponse(
        success=True,
        message="Logs queried successfully",
        data={
            "logs": [ApplicationLogResponse.model_validate(l) for l in logs],
            "total_count": total,
            "page": page,
            "page_size": page_size,
        },
    )


# =============================================================================
# TRACING ENDPOINTS
# =============================================================================
@router.post(
    "/traces",
    response_model=APIResponse[TraceSpanResponse],
    status_code=status.HTTP_201_CREATED,
)
async def record_trace_span(
    payload: TraceSpanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _role=Depends(platform_role_checker),
):
    """Submits a single trace span to record a distributed execution sequence."""
    service = ObservabilityService(db)
    span = await service.record_trace_span(current_user.organization_id, payload)
    return APIResponse(
        success=True,
        message="Trace span recorded successfully",
        data=TraceSpanResponse.model_validate(span),
    )


@router.get("/traces", response_model=APIResponse[list[TraceSpanResponse]])
async def query_traces(
    trace_id: str | None = Query(None),
    service_name: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _role=Depends(read_role_checker),
):
    """Retrieves trace spans filtering by transaction trace ID or service."""
    service = ObservabilityService(db)
    traces = await service.get_traces(
        current_user.organization_id, trace_id, service_name, status_filter
    )
    return APIResponse(
        success=True,
        message="Traces fetched successfully",
        data=[TraceSpanResponse.model_validate(t) for t in traces],
    )


@router.get("/traces/dependencies", response_model=APIResponse[list[ServiceDependency]])
async def query_service_dependency_map(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _role=Depends(read_role_checker),
):
    """Generates the service calling relationships mapping latencies and failure rates."""
    service = ObservabilityService(db)
    deps = await service.get_dependency_map(current_user.organization_id)
    return APIResponse(
        success=True,
        message="Service dependency map generated successfully",
        data=[ServiceDependency.model_validate(d) for d in deps],
    )


# =============================================================================
# ALERTS ENDPOINTS
# =============================================================================
@router.post(
    "/alerts",
    response_model=APIResponse[AlertResponse],
    status_code=status.HTTP_201_CREATED,
)
async def configure_alert_rule(
    payload: AlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _role=Depends(platform_role_checker),
):
    """Registers a threshold metric alerting rule."""
    service = ObservabilityService(db)
    alert = await service.create_alert(current_user.organization_id, payload)
    return APIResponse(
        success=True,
        message="Alert incident rule configured successfully",
        data=AlertResponse.model_validate(alert),
    )


@router.get("/alerts", response_model=APIResponse[list[AlertResponse]])
async def list_incident_alerts(
    alert_status: str | None = Query(None, alias="status"),
    severity: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _role=Depends(read_role_checker),
):
    """Lists active, acknowledged, or resolved alerts for the tenant."""
    service = ObservabilityService(db)
    alerts = await service.get_alerts(
        current_user.organization_id, alert_status, severity
    )
    return APIResponse(
        success=True,
        message="Alert incidents listed successfully",
        data=[AlertResponse.model_validate(a) for a in alerts],
    )


@router.put("/alerts/{alert_id}", response_model=APIResponse[AlertResponse])
async def update_alert_status(
    alert_id: uuid.UUID,
    payload: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _role=Depends(read_role_checker),
):
    """Updates an alert status (e.g. Acknowledge/Resolve) and registers transition audit history."""
    service = ObservabilityService(db)
    alert = await service.update_alert(
        current_user.organization_id, alert_id, payload, current_user.email
    )
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert incident not found or authorization failed",
        )
    return APIResponse(
        success=True,
        message="Alert incident updated successfully",
        data=AlertResponse.model_validate(alert),
    )


# =============================================================================
# DASHBOARDS ENDPOINTS
# =============================================================================
@router.get(
    "/dashboards/{dashboard_type}", response_model=APIResponse[DashboardConfigResponse]
)
async def retrieve_dashboard_config(
    dashboard_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _role=Depends(read_role_checker),
):
    """Retrieves custom grid layout configurations by dashboard identifier type."""
    service = ObservabilityService(db)
    config = await service.get_dashboard_config(
        current_user.organization_id, dashboard_type
    )
    if not config:
        # Return fallback default configuration
        return APIResponse(
            success=True,
            message="Default dashboard configuration layout returned",
            data=DashboardConfigResponse(
                id=uuid.uuid4(),
                organization_id=current_user.organization_id,
                name=f"Standard {dashboard_type.capitalize()} Layout",
                dashboard_type=dashboard_type,
                config={"layout": "default", "widgets": []},
                created_by="system",
                created_at=datetime.now(UTC),
            ),
        )
    return APIResponse(
        success=True,
        message="Dashboard configuration layout loaded successfully",
        data=DashboardConfigResponse.model_validate(config),
    )


@router.post(
    "/dashboards/{dashboard_type}", response_model=APIResponse[DashboardConfigResponse]
)
async def save_dashboard_config(
    dashboard_type: str,
    payload: DashboardConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _role=Depends(platform_role_checker),
):
    """Saves custom layout configurations for a specific dashboard type."""
    service = ObservabilityService(db)
    config = await service.save_dashboard_config(
        current_user.organization_id, dashboard_type, payload, current_user.email
    )
    return APIResponse(
        success=True,
        message="Dashboard configuration layout saved successfully",
        data=DashboardConfigResponse.model_validate(config),
    )


# =============================================================================
# OBSERVABILITY EVENTS
# =============================================================================
@router.get("/events", response_model=APIResponse[list[ObservabilityEventResponse]])
async def query_observability_events(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _role=Depends(read_role_checker),
):
    """Lists recent deployments, updates, database audits, and pipeline actions."""
    service = ObservabilityService(db)
    events = await service.get_events(current_user.organization_id)
    return APIResponse(
        success=True,
        message="Observability events fetched successfully",
        data=[ObservabilityEventResponse.model_validate(e) for e in events],
    )
