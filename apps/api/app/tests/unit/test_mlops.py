import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.services.mlops_service import MLOpsService
from app.models.mlops import (
    MLDeployment,
    DeploymentHistory,
    PipelineTemplate,
    PipelineRun,
    ModelApproval,
    ModelMonitoringMetric,
    DriftReport,
    RetrainingJob,
)
from app.schemas.mlops import (
    MLDeploymentCreate,
    PipelineTemplateCreate,
    PipelineRunCreate,
    ModelApprovalCreate,
    ModelApprovalUpdate,
    ModelMonitoringMetricCreate,
    DriftReportCreate,
    RetrainingJobCreate,
)


@pytest.mark.asyncio
async def test_create_deployment():
    # Setup service with mock db
    mock_db = AsyncMock()
    service = MLOpsService(mock_db)
    
    # Mock repo methods
    org_id = uuid.uuid4()
    model_id = uuid.uuid4()
    version_id = uuid.uuid4()
    
    mock_dep = MLDeployment(
        id=uuid.uuid4(),
        organization_id=org_id,
        model_id=model_id,
        model_version_id=version_id,
        name="Credit Risk Classifier",
        environment="PRODUCTION",
        status="ACTIVE",
        strategy="BLUE_GREEN",
        target_traffic_percentage=100.0,
        active_version="v1.0.0",
        endpoint_url="https://api.vertexerp.ai/ml/inference/production/deployments/credit-risk-classifier"
    )
    
    service.repo.create_deployment = AsyncMock(return_value=mock_dep)
    service.repo.create_history = AsyncMock()

    payload = MLDeploymentCreate(
        model_id=model_id,
        model_version_id=version_id,
        name="Credit Risk Classifier",
        environment="PRODUCTION",
        strategy="BLUE_GREEN",
        target_traffic_percentage=100.0
    )
    
    res = await service.create_deployment(org_id, payload, "principal.architect@vertex.ai")
    
    assert res.name == "Credit Risk Classifier"
    assert res.environment == "PRODUCTION"
    assert res.strategy == "BLUE_GREEN"
    assert service.repo.create_deployment.called
    assert service.repo.create_history.called


@pytest.mark.asyncio
async def test_update_traffic():
    mock_db = AsyncMock()
    service = MLOpsService(mock_db)
    
    dep_id = uuid.uuid4()
    mock_dep = MLDeployment(
        id=dep_id,
        model_version_id=uuid.uuid4(),
        target_traffic_percentage=100.0
    )
    
    service.repo.get_deployment_by_id = AsyncMock(return_value=mock_dep)
    service.repo.update_deployment = AsyncMock(return_value=MLDeployment(id=dep_id, target_traffic_percentage=25.0))
    service.repo.create_history = AsyncMock()
    
    updated = await service.update_traffic(dep_id, 25.0, "mlops.engineer@vertex.ai")
    
    assert updated.target_traffic_percentage == 25.0
    assert service.repo.update_deployment.called
    assert service.repo.create_history.called


@pytest.mark.asyncio
async def test_rollback_deployment():
    mock_db = AsyncMock()
    service = MLOpsService(mock_db)
    
    dep_id = uuid.uuid4()
    old_version_id = uuid.uuid4()
    stable_version_id = uuid.uuid4()
    
    mock_dep = MLDeployment(
        id=dep_id,
        model_version_id=old_version_id,
        status="ACTIVE"
    )
    
    service.repo.get_deployment_by_id = AsyncMock(return_value=mock_dep)
    service.repo.update_deployment = AsyncMock(return_value=MLDeployment(id=dep_id, model_version_id=stable_version_id, status="ACTIVE"))
    service.repo.create_history = AsyncMock()
    
    rolled_back = await service.rollback_deployment(dep_id, stable_version_id, "admin@vertex.ai")
    
    assert rolled_back.model_version_id == stable_version_id
    assert service.repo.update_deployment.called
    assert service.repo.create_history.called


@pytest.mark.asyncio
async def test_run_pipeline():
    mock_db = AsyncMock()
    service = MLOpsService(mock_db)
    
    org_id = uuid.uuid4()
    template_id = uuid.uuid4()
    run_id = uuid.uuid4()
    
    initial_run = PipelineRun(
        id=run_id,
        organization_id=org_id,
        template_id=template_id,
        run_name="Continuous Training Run #1",
        status="RUNNING",
        logs="[INFO] Initializing Pipeline Execution...\n"
    )
    
    completed_run = PipelineRun(
        id=run_id,
        organization_id=org_id,
        template_id=template_id,
        run_name="Continuous Training Run #1",
        status="COMPLETED",
        metrics_json={"validation_passed": True, "accuracy": 0.95},
        logs="[INFO] Initializing Pipeline Execution...\n[INFO] Run completed successfully.\n"
    )
    
    service.repo.create_pipeline_run = AsyncMock(return_value=initial_run)
    service.repo.update_pipeline_run = AsyncMock()
    service.repo.get_pipeline_run_by_id = AsyncMock(return_value=completed_run)
    
    payload = PipelineRunCreate(
        template_id=template_id,
        run_name="Continuous Training Run #1"
    )
    
    res = await service.run_pipeline(org_id, payload)
    
    assert res.status == "COMPLETED"
    assert res.metrics_json["validation_passed"] is True
    assert "accuracy" in res.metrics_json
    assert service.repo.create_pipeline_run.called
    assert service.repo.update_pipeline_run.called


@pytest.mark.asyncio
async def test_request_and_decide_approval():
    mock_db = AsyncMock()
    service = MLOpsService(mock_db)
    
    org_id = uuid.uuid4()
    version_id = uuid.uuid4()
    approval_id = uuid.uuid4()
    
    pending_approval = ModelApproval(
        id=approval_id,
        organization_id=org_id,
        model_version_id=version_id,
        requested_by="requester@vertex.ai",
        target_environment="STAGING",
        approval_status="PENDING"
    )
    
    approved_decision = ModelApproval(
        id=approval_id,
        organization_id=org_id,
        model_version_id=version_id,
        requested_by="requester@vertex.ai",
        target_environment="STAGING",
        approval_status="APPROVED",
        approver="architect@vertex.ai"
    )
    
    service.repo.create_approval = AsyncMock(return_value=pending_approval)
    service.repo.update_approval = AsyncMock(return_value=approved_decision)
    
    # Test request
    req_payload = ModelApprovalCreate(
        model_version_id=version_id,
        requested_by="requester@vertex.ai",
        target_environment="STAGING"
    )
    
    app_obj = await service.request_approval(org_id, req_payload)
    assert app_obj.approval_status == "PENDING"
    assert service.repo.create_approval.called
    
    # Test decision
    decision_payload = ModelApprovalUpdate(
        approval_status="APPROVED",
        approver="architect@vertex.ai",
        comments="Meets compliance benchmarks."
    )
    
    decided_obj = await service.decide_approval(approval_id, decision_payload)
    assert decided_obj.approval_status == "APPROVED"
    assert decided_obj.approver == "architect@vertex.ai"
    assert service.repo.update_approval.called


@pytest.mark.asyncio
async def test_evaluate_drift_triggers_alert():
    mock_db = AsyncMock()
    service = MLOpsService(mock_db)
    
    org_id = uuid.uuid4()
    dep_id = uuid.uuid4()
    
    # Setup mock methods
    service.repo.create_drift_report = AsyncMock(side_effect=lambda x: x)
    service.repo.get_deployment_by_id = AsyncMock(return_value=MLDeployment(id=dep_id, model_id=uuid.uuid4()))
    service.trigger_retraining_job = AsyncMock()
    
    # Low drift - should be normal
    payload_low = DriftReportCreate(
        drift_type="DATA_DRIFT",
        feature_name="satisfaction_score",
        drift_score=0.08
    )
    res_low = await service.evaluate_drift(org_id, dep_id, payload_low)
    assert res_low.status == "NORMAL"
    assert not service.trigger_retraining_job.called
    
    # High drift - should trigger retraining and warning/critical status
    payload_high = DriftReportCreate(
        drift_type="DATA_DRIFT",
        feature_name="satisfaction_score",
        drift_score=0.35
    )
    res_high = await service.evaluate_drift(org_id, dep_id, payload_high)
    assert res_high.status == "CRITICAL"
    assert service.trigger_retraining_job.called
