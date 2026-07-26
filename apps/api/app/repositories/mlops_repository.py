import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, update, delete, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
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


class MLOpsRepository:
    """Repository handling all MLOps Platform database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================================================================
    # ML DEPLOYMENTS
    # =========================================================================
    async def create_deployment(self, deployment: MLDeployment) -> MLDeployment:
        self.db.add(deployment)
        await self.db.commit()
        await self.db.refresh(deployment)
        return deployment

    async def get_deployments(self, organization_id: uuid.UUID) -> List[MLDeployment]:
        stmt = (
            select(MLDeployment)
            .where(MLDeployment.organization_id == organization_id)
            .order_by(desc(MLDeployment.created_at))
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_deployment_by_id(self, deployment_id: uuid.UUID) -> Optional[MLDeployment]:
        stmt = (
            select(MLDeployment)
            .options(selectinload(MLDeployment.history))
            .where(MLDeployment.id == deployment_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def update_deployment(self, deployment_id: uuid.UUID, values: Dict[str, Any]) -> Optional[MLDeployment]:
        stmt = (
            update(MLDeployment)
            .where(MLDeployment.id == deployment_id)
            .values(**values, updated_at=datetime.utcnow())
            .returning(MLDeployment)
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.scalar_one_or_none()

    # =========================================================================
    # DEPLOYMENT HISTORY
    # =========================================================================
    async def create_history(self, history: DeploymentHistory) -> DeploymentHistory:
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def get_history_by_deployment(self, deployment_id: uuid.UUID) -> List[DeploymentHistory]:
        stmt = (
            select(DeploymentHistory)
            .where(DeploymentHistory.deployment_id == deployment_id)
            .order_by(desc(DeploymentHistory.created_at))
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # =========================================================================
    # PIPELINE TEMPLATES
    # =========================================================================
    async def create_pipeline_template(self, template: PipelineTemplate) -> PipelineTemplate:
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template

    async def get_pipeline_templates(self, organization_id: uuid.UUID) -> List[PipelineTemplate]:
        stmt = (
            select(PipelineTemplate)
            .where(PipelineTemplate.organization_id == organization_id)
            .order_by(desc(PipelineTemplate.created_at))
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_pipeline_template_by_id(self, template_id: uuid.UUID) -> Optional[PipelineTemplate]:
        stmt = select(PipelineTemplate).where(PipelineTemplate.id == template_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    # =========================================================================
    # PIPELINE RUNS
    # =========================================================================
    async def create_pipeline_run(self, run: PipelineRun) -> PipelineRun:
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def get_pipeline_runs(self, organization_id: uuid.UUID) -> List[PipelineRun]:
        stmt = (
            select(PipelineRun)
            .where(PipelineRun.organization_id == organization_id)
            .order_by(desc(PipelineRun.created_at))
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_pipeline_run_by_id(self, run_id: uuid.UUID) -> Optional[PipelineRun]:
        stmt = select(PipelineRun).where(PipelineRun.id == run_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def update_pipeline_run(self, run_id: uuid.UUID, values: Dict[str, Any]) -> Optional[PipelineRun]:
        stmt = (
            update(PipelineRun)
            .where(PipelineRun.id == run_id)
            .values(**values)
            .returning(PipelineRun)
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.scalar_one_or_none()

    # =========================================================================
    # MODEL APPROVALS
    # =========================================================================
    async def create_approval(self, approval: ModelApproval) -> ModelApproval:
        self.db.add(approval)
        await self.db.commit()
        await self.db.refresh(approval)
        return approval

    async def get_approvals(self, organization_id: uuid.UUID, status: Optional[str] = None) -> List[ModelApproval]:
        stmt = select(ModelApproval).where(ModelApproval.organization_id == organization_id)
        if status:
            stmt = stmt.where(ModelApproval.approval_status == status)
        stmt = stmt.order_by(desc(ModelApproval.request_date))
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_approval_by_id(self, approval_id: uuid.UUID) -> Optional[ModelApproval]:
        stmt = select(ModelApproval).where(ModelApproval.id == approval_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def update_approval(self, approval_id: uuid.UUID, values: Dict[str, Any]) -> Optional[ModelApproval]:
        stmt = (
            update(ModelApproval)
            .where(ModelApproval.id == approval_id)
            .values(**values)
            .returning(ModelApproval)
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.scalar_one_or_none()

    # =========================================================================
    # MODEL MONITORING METRICS
    # =========================================================================
    async def create_monitoring_metric(self, metric: ModelMonitoringMetric) -> ModelMonitoringMetric:
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        return metric

    async def get_monitoring_metrics(self, organization_id: uuid.UUID, deployment_id: uuid.UUID, limit: int = 100) -> List[ModelMonitoringMetric]:
        stmt = (
            select(ModelMonitoringMetric)
            .where(ModelMonitoringMetric.organization_id == organization_id, ModelMonitoringMetric.deployment_id == deployment_id)
            .order_by(desc(ModelMonitoringMetric.timestamp))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # =========================================================================
    # DRIFT REPORTS
    # =========================================================================
    async def create_drift_report(self, report: DriftReport) -> DriftReport:
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_drift_reports(self, organization_id: uuid.UUID, deployment_id: uuid.UUID) -> List[DriftReport]:
        stmt = (
            select(DriftReport)
            .where(DriftReport.organization_id == organization_id, DriftReport.deployment_id == deployment_id)
            .order_by(desc(DriftReport.created_at))
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # =========================================================================
    # RETRAINING JOBS
    # =========================================================================
    async def create_retraining_job(self, job: RetrainingJob) -> RetrainingJob:
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get_retraining_jobs(self, organization_id: uuid.UUID, model_id: Optional[uuid.UUID] = None) -> List[RetrainingJob]:
        stmt = select(RetrainingJob).where(RetrainingJob.organization_id == organization_id)
        if model_id:
            stmt = stmt.where(RetrainingJob.model_id == model_id)
        stmt = stmt.order_by(desc(RetrainingJob.created_at))
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_retraining_job_by_id(self, job_id: uuid.UUID) -> Optional[RetrainingJob]:
        stmt = select(RetrainingJob).where(RetrainingJob.id == job_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def update_retraining_job(self, job_id: uuid.UUID, values: Dict[str, Any]) -> Optional[RetrainingJob]:
        stmt = (
            update(RetrainingJob)
            .where(RetrainingJob.id == job_id)
            .values(**values)
            .returning(RetrainingJob)
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.scalar_one_or_none()
