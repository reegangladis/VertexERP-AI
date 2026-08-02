import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.workflow import (
    ApprovalHistory,
    ApprovalRequest,
    BusinessRule,
    ScheduledJob,
    Workflow,
    WorkflowExecution,
    WorkflowLog,
    WorkflowStep,
    WorkflowTemplate,
    WorkflowVersion,
)


class WorkflowRepository:
    """Data access layer for workflow automation models with tenant-scoped queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ─── Workflow CRUD ───────────────────────────────────────────────────────────
    async def create_workflow(
        self, org_id: uuid.UUID | None, data: dict[str, Any]
    ) -> Workflow:
        obj = Workflow(organization_id=org_id, **data)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def get_workflow(
        self, org_id: uuid.UUID | None, workflow_id: uuid.UUID
    ) -> Workflow | None:
        stmt = select(Workflow).where(
            and_(Workflow.id == workflow_id, Workflow.organization_id == org_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_workflows(
        self,
        org_id: uuid.UUID | None,
        status: str | None = None,
        category: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Workflow]:
        conditions = [Workflow.organization_id == org_id]
        if status:
            conditions.append(Workflow.status == status)
        if category:
            conditions.append(Workflow.category == category)
        stmt = (
            select(Workflow)
            .where(and_(*conditions))
            .order_by(desc(Workflow.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_workflow(
        self, workflow: Workflow, updates: dict[str, Any]
    ) -> Workflow:
        for k, v in updates.items():
            setattr(workflow, k, v)
        self.db.add(workflow)
        await self.db.flush()
        await self.db.refresh(workflow)
        return workflow

    async def delete_workflow(self, workflow: Workflow) -> None:
        await self.db.delete(workflow)
        await self.db.flush()

    # ─── Versions ────────────────────────────────────────────────────────────────
    async def create_version(
        self, org_id: uuid.UUID | None, data: dict[str, Any]
    ) -> WorkflowVersion:
        obj = WorkflowVersion(organization_id=org_id, **data)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def get_version(self, version_id: uuid.UUID) -> WorkflowVersion | None:
        result = await self.db.execute(
            select(WorkflowVersion).where(WorkflowVersion.id == version_id)
        )
        return result.scalar_one_or_none()

    async def list_versions(self, workflow_id: uuid.UUID) -> list[WorkflowVersion]:
        stmt = (
            select(WorkflowVersion)
            .where(WorkflowVersion.workflow_id == workflow_id)
            .order_by(desc(WorkflowVersion.created_at))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def publish_version(self, version: WorkflowVersion) -> WorkflowVersion:
        version.is_published = True
        self.db.add(version)
        await self.db.flush()
        await self.db.refresh(version)
        return version

    # ─── Executions ──────────────────────────────────────────────────────────────
    async def create_execution(
        self, org_id: uuid.UUID | None, data: dict[str, Any]
    ) -> WorkflowExecution:
        obj = WorkflowExecution(organization_id=org_id, **data)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def get_execution(self, execution_id: uuid.UUID) -> WorkflowExecution | None:
        stmt = select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_execution_with_steps(
        self, execution_id: uuid.UUID
    ) -> WorkflowExecution | None:
        stmt = (
            select(WorkflowExecution)
            .where(WorkflowExecution.id == execution_id)
            .options(
                selectinload(WorkflowExecution.steps),
                selectinload(WorkflowExecution.logs),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_executions(
        self,
        org_id: uuid.UUID | None,
        workflow_id: uuid.UUID | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[WorkflowExecution]:
        conditions: list = [WorkflowExecution.organization_id == org_id]
        if workflow_id:
            conditions.append(WorkflowExecution.workflow_id == workflow_id)
        if status:
            conditions.append(WorkflowExecution.status == status)
        stmt = (
            select(WorkflowExecution)
            .where(and_(*conditions))
            .order_by(desc(WorkflowExecution.start_time))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_execution(
        self, execution: WorkflowExecution, updates: dict[str, Any]
    ) -> WorkflowExecution:
        for k, v in updates.items():
            setattr(execution, k, v)
        self.db.add(execution)
        await self.db.flush()
        await self.db.refresh(execution)
        return execution

    # ─── Steps ───────────────────────────────────────────────────────────────────
    async def create_step(
        self, org_id: uuid.UUID | None, data: dict[str, Any]
    ) -> WorkflowStep:
        obj = WorkflowStep(organization_id=org_id, **data)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update_step(
        self, step: WorkflowStep, updates: dict[str, Any]
    ) -> WorkflowStep:
        for k, v in updates.items():
            setattr(step, k, v)
        self.db.add(step)
        await self.db.flush()
        await self.db.refresh(step)
        return step

    async def list_steps(self, execution_id: uuid.UUID) -> list[WorkflowStep]:
        stmt = (
            select(WorkflowStep)
            .where(WorkflowStep.execution_id == execution_id)
            .order_by(WorkflowStep.created_at)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ─── Templates ───────────────────────────────────────────────────────────────
    async def create_template(
        self, org_id: uuid.UUID | None, data: dict[str, Any]
    ) -> WorkflowTemplate:
        obj = WorkflowTemplate(organization_id=org_id, **data)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def list_templates(
        self, org_id: uuid.UUID | None, category: str | None = None
    ) -> list[WorkflowTemplate]:
        conditions: list = [
            (WorkflowTemplate.organization_id == org_id)
            | (WorkflowTemplate.is_system == True)
        ]
        if category:
            conditions.append(WorkflowTemplate.category == category)
        stmt = (
            select(WorkflowTemplate)
            .where(and_(*conditions))
            .order_by(WorkflowTemplate.name)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_template(self, template_id: uuid.UUID) -> WorkflowTemplate | None:
        result = await self.db.execute(
            select(WorkflowTemplate).where(WorkflowTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    # ─── Business Rules ──────────────────────────────────────────────────────────
    async def create_rule(
        self, org_id: uuid.UUID | None, data: dict[str, Any]
    ) -> BusinessRule:
        obj = BusinessRule(organization_id=org_id, **data)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def get_rule(
        self, org_id: uuid.UUID | None, rule_id: uuid.UUID
    ) -> BusinessRule | None:
        result = await self.db.execute(
            select(BusinessRule).where(
                and_(BusinessRule.id == rule_id, BusinessRule.organization_id == org_id)
            )
        )
        return result.scalar_one_or_none()

    async def list_rules(
        self,
        org_id: uuid.UUID | None,
        rule_group: str | None = None,
        is_active: bool | None = None,
    ) -> list[BusinessRule]:
        conditions: list = [BusinessRule.organization_id == org_id]
        if rule_group:
            conditions.append(BusinessRule.rule_group == rule_group)
        if is_active is not None:
            conditions.append(BusinessRule.is_active == is_active)
        stmt = (
            select(BusinessRule)
            .where(and_(*conditions))
            .order_by(BusinessRule.priority)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_rule(
        self, rule: BusinessRule, updates: dict[str, Any]
    ) -> BusinessRule:
        for k, v in updates.items():
            setattr(rule, k, v)
        self.db.add(rule)
        await self.db.flush()
        await self.db.refresh(rule)
        return rule

    async def delete_rule(self, rule: BusinessRule) -> None:
        await self.db.delete(rule)
        await self.db.flush()

    # ─── Approvals ───────────────────────────────────────────────────────────────
    async def create_approval(
        self, org_id: uuid.UUID | None, data: dict[str, Any]
    ) -> ApprovalRequest:
        obj = ApprovalRequest(organization_id=org_id, **data)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def get_approval(
        self, org_id: uuid.UUID | None, approval_id: uuid.UUID
    ) -> ApprovalRequest | None:
        result = await self.db.execute(
            select(ApprovalRequest)
            .where(
                and_(
                    ApprovalRequest.id == approval_id,
                    ApprovalRequest.organization_id == org_id,
                )
            )
            .options(selectinload(ApprovalRequest.history))
        )
        return result.scalar_one_or_none()

    async def list_approvals(
        self,
        org_id: uuid.UUID | None,
        approver_id: str | None = None,
        requester_id: str | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ApprovalRequest]:
        conditions: list = [ApprovalRequest.organization_id == org_id]
        if approver_id:
            conditions.append(ApprovalRequest.approver_id == approver_id)
        if requester_id:
            conditions.append(ApprovalRequest.requester_id == requester_id)
        if status:
            conditions.append(ApprovalRequest.status == status)
        stmt = (
            select(ApprovalRequest)
            .where(and_(*conditions))
            .order_by(desc(ApprovalRequest.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_approval(
        self, approval: ApprovalRequest, updates: dict[str, Any]
    ) -> ApprovalRequest:
        for k, v in updates.items():
            setattr(approval, k, v)
        self.db.add(approval)
        await self.db.flush()
        await self.db.refresh(approval)
        return approval

    async def create_approval_history(
        self, org_id: uuid.UUID | None, data: dict[str, Any]
    ) -> ApprovalHistory:
        obj = ApprovalHistory(organization_id=org_id, **data)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def list_approval_history(
        self, approval_request_id: uuid.UUID
    ) -> list[ApprovalHistory]:
        stmt = (
            select(ApprovalHistory)
            .where(ApprovalHistory.approval_request_id == approval_request_id)
            .order_by(ApprovalHistory.created_at)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ─── Scheduled Jobs ──────────────────────────────────────────────────────────
    async def create_scheduled_job(
        self, org_id: uuid.UUID | None, data: dict[str, Any]
    ) -> ScheduledJob:
        obj = ScheduledJob(organization_id=org_id, **data)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def get_scheduled_job(
        self, org_id: uuid.UUID | None, job_id: uuid.UUID
    ) -> ScheduledJob | None:
        result = await self.db.execute(
            select(ScheduledJob).where(
                and_(ScheduledJob.id == job_id, ScheduledJob.organization_id == org_id)
            )
        )
        return result.scalar_one_or_none()

    async def list_scheduled_jobs(
        self,
        org_id: uuid.UUID | None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ScheduledJob]:
        conditions: list = [ScheduledJob.organization_id == org_id]
        if status:
            conditions.append(ScheduledJob.status == status)
        stmt = (
            select(ScheduledJob)
            .where(and_(*conditions))
            .order_by(ScheduledJob.next_run_at)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_scheduled_job(
        self, job: ScheduledJob, updates: dict[str, Any]
    ) -> ScheduledJob:
        for k, v in updates.items():
            setattr(job, k, v)
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def delete_scheduled_job(self, job: ScheduledJob) -> None:
        await self.db.delete(job)
        await self.db.flush()

    async def get_due_scheduled_jobs(self, now: datetime) -> list[ScheduledJob]:
        stmt = select(ScheduledJob).where(
            and_(
                ScheduledJob.status == "active",
                ScheduledJob.next_run_at <= now,
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ─── Logs ────────────────────────────────────────────────────────────────────
    async def create_log(
        self, org_id: uuid.UUID | None, data: dict[str, Any]
    ) -> WorkflowLog:
        obj = WorkflowLog(organization_id=org_id, **data)
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def list_logs(
        self,
        execution_id: uuid.UUID,
        log_level: str | None = None,
        skip: int = 0,
        limit: int = 200,
    ) -> list[WorkflowLog]:
        conditions: list = [WorkflowLog.execution_id == execution_id]
        if log_level:
            conditions.append(WorkflowLog.log_level == log_level)
        stmt = (
            select(WorkflowLog)
            .where(and_(*conditions))
            .order_by(WorkflowLog.timestamp)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
