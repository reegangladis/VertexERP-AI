import uuid
from datetime import datetime, UTC
import random
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.repositories.mlops_repository import MLOpsRepository
from app.schemas.mlops import (
    MLDeploymentCreate,
    MLDeploymentUpdate,
    PipelineTemplateCreate,
    PipelineRunCreate,
    ModelApprovalCreate,
    ModelApprovalUpdate,
    ModelMonitoringMetricCreate,
    DriftReportCreate,
    RetrainingJobCreate,
)


class MLOpsService:
    """Core Service managing business logic for the VertexERP AI MLOps Platform."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MLOpsRepository(db)

    # =========================================================================
    # ML DEPLOYMENT SERVICES
    # =========================================================================
    async def create_deployment(self, organization_id: uuid.UUID, payload: MLDeploymentCreate, username: str) -> MLDeployment:
        # Construct endpoint URL dynamically based on environment
        env_lower = payload.environment.lower()
        endpoint_url = f"https://api.vertexerp.ai/ml/inference/{env_lower}/deployments/{payload.name.replace(' ', '-').lower()}"
        
        deployment = MLDeployment(
            organization_id=organization_id,
            model_id=payload.model_id,
            model_version_id=payload.model_version_id,
            name=payload.name,
            environment=payload.environment,
            status="ACTIVE",
            strategy=payload.strategy,
            target_traffic_percentage=payload.target_traffic_percentage or 100.0,
            active_version="v1.0.0",  # Default baseline version
            endpoint_url=endpoint_url,
            config_json=payload.config_json or {},
        )
        created_dep = await self.repo.create_deployment(deployment)

        # Audit history log
        history = DeploymentHistory(
            deployment_id=created_dep.id,
            previous_version_id=None,
            new_version_id=payload.model_version_id,
            action="CREATE",
            status="SUCCESS",
            triggered_by=username,
            notes=f"Deployment endpoint initialized in {payload.environment} using strategy {payload.strategy}.",
        )
        await self.repo.create_history(history)
        
        return created_dep

    async def get_deployments(self, organization_id: uuid.UUID) -> List[MLDeployment]:
        return await self.repo.get_deployments(organization_id)

    async def get_deployment_by_id(self, deployment_id: uuid.UUID) -> Optional[MLDeployment]:
        return await self.repo.get_deployment_by_id(deployment_id)

    async def update_traffic(self, deployment_id: uuid.UUID, traffic_pct: float, username: str) -> Optional[MLDeployment]:
        dep = await self.repo.get_deployment_by_id(deployment_id)
        if not dep:
            return None

        updated_dep = await self.repo.update_deployment(
            deployment_id,
            {"target_traffic_percentage": traffic_pct}
        )

        history = DeploymentHistory(
            deployment_id=deployment_id,
            previous_version_id=dep.model_version_id,
            new_version_id=dep.model_version_id,
            action="UPDATE",
            status="SUCCESS",
            triggered_by=username,
            notes=f"Traffic routing configuration modified. Target traffic split updated to {traffic_pct}%.",
        )
        await self.repo.create_history(history)
        return updated_dep

    async def rollback_deployment(self, deployment_id: uuid.UUID, target_version_id: uuid.UUID, username: str, notes: Optional[str] = None) -> Optional[MLDeployment]:
        dep = await self.repo.get_deployment_by_id(deployment_id)
        if not dep:
            return None

        previous_version_id = dep.model_version_id
        updated_dep = await self.repo.update_deployment(
            deployment_id,
            {"model_version_id": target_version_id, "status": "ACTIVE"}
        )

        history = DeploymentHistory(
            deployment_id=deployment_id,
            previous_version_id=previous_version_id,
            new_version_id=target_version_id,
            action="ROLLBACK",
            status="SUCCESS",
            triggered_by=username,
            notes=notes or f"Deployment rolled back to previous stable model version ID: {target_version_id}.",
        )
        await self.repo.create_history(history)
        return updated_dep

    # =========================================================================
    # PIPELINE SERVICES
    # =========================================================================
    async def create_pipeline_template(self, organization_id: uuid.UUID, payload: PipelineTemplateCreate) -> PipelineTemplate:
        template = PipelineTemplate(
            organization_id=organization_id,
            name=payload.name,
            description=payload.description,
            pipeline_type=payload.pipeline_type,
            version=payload.version,
            definition_json=payload.definition_json or {},
            is_active=True
        )
        return await self.repo.create_pipeline_template(template)

    async def get_pipeline_templates(self, organization_id: uuid.UUID) -> List[PipelineTemplate]:
        return await self.repo.get_pipeline_templates(organization_id)

    async def get_pipeline_template_by_id(self, template_id: uuid.UUID) -> Optional[PipelineTemplate]:
        return await self.repo.get_pipeline_template_by_id(template_id)

    async def run_pipeline(self, organization_id: uuid.UUID, payload: PipelineRunCreate) -> PipelineRun:
        # Initialize pipeline run
        run = PipelineRun(
            organization_id=organization_id,
            template_id=payload.template_id,
            model_id=payload.model_id,
            model_version_id=payload.model_version_id,
            run_name=payload.run_name,
            status="RUNNING",
            metrics_json={},
            logs="[INFO] Initializing Pipeline Execution...\n"
        )
        created_run = await self.repo.create_pipeline_run(run)

        # Simulate Pipeline Stages synchronously for demonstration/mock validation
        logs = created_run.logs
        logs += f"[INFO] Fetching pipeline template config...\n"
        logs += f"[INFO] Commencing Continuous Integration validation checks...\n"
        
        # Check standard validations
        validation_passed = True
        if random.random() < 0.05:  # 5% chance of failing validation
            validation_passed = False
            logs += f"[ERROR] Artifact validation failed: checksum verification error.\n"
            logs += f"[ERROR] Pipeline execution terminated due to errors.\n"
            status = "FAILED"
            metrics = {"validation_passed": False, "accuracy": 0.0}
        else:
            logs += f"[INFO] Artifact validation check: SUCCESS.\n"
            logs += f"[INFO] Running security signature scan...\n"
            logs += f"[INFO] Vulnerability check: No threat detected. SUCCESS.\n"
            logs += f"[INFO] Loading datasets and training adaptation configurations...\n"
            logs += f"[INFO] Epoch 1/5: loss=0.45, accuracy=0.81\n"
            logs += f"[INFO] Epoch 5/5: loss=0.12, accuracy=0.96\n"
            logs += f"[INFO] Running Continuous Validation checks against evaluation baseline...\n"
            logs += f"[INFO] Promotion checks: Model validation passed successfully.\n"
            logs += f"[INFO] Pipeline Run completed successfully.\n"
            status = "COMPLETED"
            metrics = {
                "validation_passed": True,
                "accuracy": round(random.uniform(0.92, 0.98), 4),
                "f1_score": round(random.uniform(0.91, 0.97), 4),
                "roc_auc": round(random.uniform(0.94, 0.99), 4),
            }

        await self.repo.update_pipeline_run(
            created_run.id,
            {
                "status": status,
                "logs": logs,
                "metrics_json": metrics,
                "completed_at": datetime.now(UTC),
            }
        )
        return await self.repo.get_pipeline_run_by_id(created_run.id)

    async def get_pipeline_runs(self, organization_id: uuid.UUID) -> List[PipelineRun]:
        return await self.repo.get_pipeline_runs(organization_id)

    async def get_pipeline_run_by_id(self, run_id: uuid.UUID) -> Optional[PipelineRun]:
        return await self.repo.get_pipeline_run_by_id(run_id)

    # =========================================================================
    # MODEL GOVERNANCE & APPROVALS
    # =========================================================================
    async def request_approval(self, organization_id: uuid.UUID, payload: ModelApprovalCreate) -> ModelApproval:
        # Default compliance structure if not provided
        compliance = payload.compliance_metadata_json or {
            "bias_checked": True,
            "explainability_report_available": True,
            "security_hardened": True,
            "license_verified": True,
            "ownership_team": "ML Platform Engineering",
            "model_card_url": "https://vertexerp.ai/governance/cards/mdl-v1"
        }
        
        approval = ModelApproval(
            organization_id=organization_id,
            model_version_id=payload.model_version_id,
            request_date=datetime.now(UTC),
            requested_by=payload.requested_by,
            target_environment=payload.target_environment,
            approval_status="PENDING",
            compliance_metadata_json=compliance,
            comments=payload.comments
        )
        return await self.repo.create_approval(approval)

    async def list_approval_queue(self, organization_id: uuid.UUID, status: Optional[str] = None) -> List[ModelApproval]:
        return await self.repo.get_approvals(organization_id, status)

    async def decide_approval(self, approval_id: uuid.UUID, payload: ModelApprovalUpdate) -> Optional[ModelApproval]:
        return await self.repo.update_approval(
            approval_id,
            {
                "approval_status": payload.approval_status,
                "approver": payload.approver,
                "comments": payload.comments,
                "decision_date": datetime.now(UTC)
            }
        )

    # =========================================================================
    # MODEL MONITORING & OBSERVE
    # =========================================================================
    async def ingest_metric(self, organization_id: uuid.UUID, deployment_id: uuid.UUID, payload: ModelMonitoringMetricCreate) -> ModelMonitoringMetric:
        metric = ModelMonitoringMetric(
            organization_id=organization_id,
            deployment_id=deployment_id,
            metric_name=payload.metric_name,
            metric_value=payload.metric_value,
            timestamp=datetime.now(UTC)
        )
        return await self.repo.create_monitoring_metric(metric)

    async def get_metrics(self, organization_id: uuid.UUID, deployment_id: uuid.UUID, limit: int = 100) -> List[ModelMonitoringMetric]:
        return await self.repo.get_monitoring_metrics(organization_id, deployment_id, limit)

    async def evaluate_drift(self, organization_id: uuid.UUID, deployment_id: uuid.UUID, payload: DriftReportCreate) -> DriftReport:
        # Check drift status based on score threshold
        status = "NORMAL"
        if payload.drift_score >= 0.25:
            status = "CRITICAL"
        elif payload.drift_score >= 0.1:
            status = "WARNING"

        metrics = payload.metrics_json or {
            "ks_statistic": round(payload.drift_score * 0.9, 4),
            "p_value": round(0.05 / (payload.drift_score + 0.001), 4),
            "psi_score": round(payload.drift_score * 1.2, 4)
        }

        report = DriftReport(
            organization_id=organization_id,
            deployment_id=deployment_id,
            drift_type=payload.drift_type,
            feature_name=payload.feature_name,
            drift_score=payload.drift_score,
            status=status,
            metrics_json=metrics
        )
        
        created_report = await self.repo.create_drift_report(report)

        # Trigger auto-retraining if drift is CRITICAL
        if status == "CRITICAL":
            # Find the deployment model ID
            dep = await self.repo.get_deployment_by_id(deployment_id)
            if dep:
                await self.trigger_retraining_job(
                    organization_id=organization_id,
                    payload=RetrainingJobCreate(
                        model_id=dep.model_id,
                        trigger_type="DRIFT_TRIGGERED",
                        config_json={"drift_report_id": str(created_report.id)}
                    )
                )

        return created_report

    async def get_drift_reports(self, organization_id: uuid.UUID, deployment_id: uuid.UUID) -> List[DriftReport]:
        return await self.repo.get_drift_reports(organization_id, deployment_id)

    # =========================================================================
    # MODEL RETRAINING SERVICES
    # =========================================================================
    async def trigger_retraining_job(self, organization_id: uuid.UUID, payload: RetrainingJobCreate) -> RetrainingJob:
        job = RetrainingJob(
            organization_id=organization_id,
            model_id=payload.model_id,
            trigger_type=payload.trigger_type,
            status="RUNNING",
            config_json=payload.config_json or {},
        )
        created_job = await self.repo.create_retraining_job(job)

        # Simulate Retraining process execution
        status = "COMPLETED"
        error_msg = None
        
        # 5% chance of mock failure
        if random.random() < 0.05:
            status = "FAILED"
            error_msg = "Data loading failed: out of memory error during GPU dataset cache allocation."

        await self.repo.update_retraining_job(
            created_job.id,
            {
                "status": status,
                "error_message": error_msg,
                "completed_at": datetime.now(UTC),
            }
        )
        return await self.repo.get_retraining_job_by_id(created_job.id)

    async def get_retraining_jobs(self, organization_id: uuid.UUID, model_id: Optional[uuid.UUID] = None) -> List[RetrainingJob]:
        return await self.repo.get_retraining_jobs(organization_id, model_id)

    async def get_retraining_job_by_id(self, job_id: uuid.UUID) -> Optional[RetrainingJob]:
        return await self.repo.get_retraining_job_by_id(job_id)
