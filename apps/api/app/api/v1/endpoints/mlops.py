import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.mlops import (
    DeploymentRollbackRequest,
    DeploymentTrafficUpdate,
    DriftReportCreate,
    DriftReportResponse,
    MLDeploymentCreate,
    MLDeploymentResponse,
    ModelApprovalCreate,
    ModelApprovalResponse,
    ModelApprovalUpdate,
    ModelMonitoringMetricCreate,
    ModelMonitoringMetricResponse,
    PipelineRunCreate,
    PipelineRunResponse,
    PipelineTemplateCreate,
    PipelineTemplateResponse,
    RetrainingJobCreate,
    RetrainingJobResponse,
)
from app.services.mlops_service import MLOpsService

router = APIRouter()


# =============================================================================
# DEPLOYMENT ENDPOINTS
# =============================================================================
@router.post(
    "/deployments",
    response_model=MLDeploymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_deployment(
    payload: MLDeploymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deploys a machine learning model to a specified environment and records deployment audit history."""
    service = MLOpsService(db)
    return await service.create_deployment(
        current_user.organization_id, payload, current_user.email
    )


@router.get("/deployments", response_model=list[MLDeploymentResponse])
async def list_deployments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists all active and historical deployments for the current organization."""
    service = MLOpsService(db)
    return await service.get_deployments(current_user.organization_id)


@router.get("/deployments/{deployment_id}", response_model=MLDeploymentResponse)
async def get_deployment(
    deployment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves detailed deployment information including configuration and lifecycle audit logs."""
    service = MLOpsService(db)
    dep = await service.get_deployment_by_id(deployment_id)
    if not dep:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return dep


@router.put("/deployments/{deployment_id}/traffic", response_model=MLDeploymentResponse)
async def update_traffic(
    deployment_id: uuid.UUID,
    payload: DeploymentTrafficUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Modifies the active traffic routing percentage splits for Blue-Green or Canary configurations."""
    service = MLOpsService(db)
    updated = await service.update_traffic(
        deployment_id, payload.target_traffic_percentage, current_user.email
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return updated


@router.post(
    "/deployments/{deployment_id}/rollback", response_model=MLDeploymentResponse
)
async def rollback_deployment(
    deployment_id: uuid.UUID,
    payload: DeploymentRollbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Triggers an instant rollback of the deployment to a target stable model version."""
    service = MLOpsService(db)
    rolled_back = await service.rollback_deployment(
        deployment_id, payload.target_version_id, current_user.email, payload.notes
    )
    if not rolled_back:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return rolled_back


# =============================================================================
# PIPELINE ENDPOINTS
# =============================================================================
@router.post(
    "/pipelines/templates",
    response_model=PipelineTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_pipeline_template(
    payload: PipelineTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Registers a reusable versioned Pipeline Template (e.g. training, continuous validation)."""
    service = MLOpsService(db)
    return await service.create_pipeline_template(current_user.organization_id, payload)


@router.get("/pipelines/templates", response_model=list[PipelineTemplateResponse])
async def list_pipeline_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists all available pipeline templates."""
    service = MLOpsService(db)
    return await service.get_pipeline_templates(current_user.organization_id)


@router.post(
    "/pipelines/runs",
    response_model=PipelineRunResponse,
    status_code=status.HTTP_201_CREATED,
)
async def trigger_pipeline_run(
    payload: PipelineRunCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Executes a pipeline template run with automated testing, validation and code metrics parsing."""
    service = MLOpsService(db)
    return await service.run_pipeline(current_user.organization_id, payload)


@router.get("/pipelines/runs", response_model=list[PipelineRunResponse])
async def list_pipeline_runs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists recent pipeline run executions, outcomes, and execution times."""
    service = MLOpsService(db)
    return await service.get_pipeline_runs(current_user.organization_id)


@router.get("/pipelines/runs/{run_id}", response_model=PipelineRunResponse)
async def get_pipeline_run(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetches full status, metrics summary, and printed execution logs of a pipeline run."""
    service = MLOpsService(db)
    run = await service.get_pipeline_run_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    return run


# =============================================================================
# MODEL GOVERNANCE & PROMOTIONS
# =============================================================================
@router.post(
    "/approvals",
    response_model=ModelApprovalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def request_promotion_approval(
    payload: ModelApprovalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submits a promotion request to deploy a model version to testing, staging or production."""
    service = MLOpsService(db)
    return await service.request_approval(current_user.organization_id, payload)


@router.get("/approvals", response_model=list[ModelApprovalResponse])
async def list_approvals(
    status: str | None = Query(
        None, description="Filter queue: PENDING, APPROVED, REJECTED"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists requests in the model promotion governance queue."""
    service = MLOpsService(db)
    return await service.list_approval_queue(current_user.organization_id, status)


@router.post("/approvals/{approval_id}/decide", response_model=ModelApprovalResponse)
async def decide_approval(
    approval_id: uuid.UUID,
    payload: ModelApprovalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approves or rejects a model promotion request, logging decisions and comments in the audit trail."""
    service = MLOpsService(db)
    decision = await service.decide_approval(approval_id, payload)
    if not decision:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return decision


# =============================================================================
# MODEL MONITORING & DRIFT ENDPOINTS
# =============================================================================
@router.post(
    "/monitoring/{deployment_id}/metrics",
    response_model=ModelMonitoringMetricResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ingest_telemetry_metric(
    deployment_id: uuid.UUID,
    payload: ModelMonitoringMetricCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ingests CPU, memory, and performance latency telemetry for a deployed deployment endpoint."""
    service = MLOpsService(db)
    return await service.ingest_metric(
        current_user.organization_id, deployment_id, payload
    )


@router.get(
    "/monitoring/{deployment_id}/metrics",
    response_model=list[ModelMonitoringMetricResponse],
)
async def list_telemetry_metrics(
    deployment_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves logged operational performance indicators for a deployment."""
    service = MLOpsService(db)
    return await service.get_metrics(current_user.organization_id, deployment_id, limit)


@router.post(
    "/monitoring/{deployment_id}/drift",
    response_model=DriftReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def evaluate_drift(
    deployment_id: uuid.UUID,
    payload: DriftReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Evaluates features and predictions for statistical drift, generating alerts or triggering retraining if critical."""
    service = MLOpsService(db)
    return await service.evaluate_drift(
        current_user.organization_id, deployment_id, payload
    )


@router.get(
    "/monitoring/{deployment_id}/drift", response_model=list[DriftReportResponse]
)
async def list_drift_reports(
    deployment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists generated data drift and prediction distribution drift reports for a deployment."""
    service = MLOpsService(db)
    return await service.get_drift_reports(current_user.organization_id, deployment_id)


# =============================================================================
# MODEL RETRAINING ENDPOINTS
# =============================================================================
@router.post(
    "/retraining",
    response_model=RetrainingJobResponse,
    status_code=status.HTTP_201_CREATED,
)
async def trigger_retraining(
    payload: RetrainingJobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually triggers or tests retraining logic on a selected baseline model."""
    service = MLOpsService(db)
    return await service.trigger_retraining_job(current_user.organization_id, payload)


@router.get("/retraining", response_model=list[RetrainingJobResponse])
async def list_retraining_history(
    model_id: uuid.UUID | None = Query(
        None, description="Filter retraining history by Model ID"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves retraining executions and trigger audits."""
    service = MLOpsService(db)
    return await service.get_retraining_jobs(current_user.organization_id, model_id)
