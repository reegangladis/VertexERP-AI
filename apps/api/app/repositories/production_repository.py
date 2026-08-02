import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.production import (
    BackupJob,
    ComplianceReport,
    LoadTestResult,
    PerformanceReport,
    RestoreJob,
    SecurityAuditLog,
)


class ProductionRepository:
    """Async SQLAlchemy repository for Production Readiness, Security, and Compliance operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ----------------------------------------------------
    # Security Audit Operations
    # ----------------------------------------------------
    async def log_security_event(self, log: SecurityAuditLog) -> SecurityAuditLog:
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def list_security_audit_logs(
        self,
        org_id: uuid.UUID | None = None,
        severity: str | None = None,
        limit: int = 100,
    ) -> list[SecurityAuditLog]:
        stmt = select(SecurityAuditLog)
        if org_id:
            stmt = stmt.where(SecurityAuditLog.organization_id == org_id)
        if severity:
            stmt = stmt.where(SecurityAuditLog.severity == severity)
        stmt = stmt.order_by(SecurityAuditLog.timestamp.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ----------------------------------------------------
    # Backup & Restore Operations
    # ----------------------------------------------------
    async def create_backup_job(self, job: BackupJob) -> BackupJob:
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def list_backup_jobs(
        self, org_id: uuid.UUID | None = None, limit: int = 50
    ) -> list[BackupJob]:
        stmt = select(BackupJob)
        if org_id:
            stmt = stmt.where(BackupJob.organization_id == org_id)
        stmt = stmt.order_by(BackupJob.created_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_backup_job_by_id(self, backup_id: uuid.UUID) -> BackupJob | None:
        stmt = select(BackupJob).where(BackupJob.id == backup_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_restore_job(self, job: RestoreJob) -> RestoreJob:
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def list_restore_jobs(
        self, org_id: uuid.UUID | None = None, limit: int = 50
    ) -> list[RestoreJob]:
        stmt = select(RestoreJob)
        if org_id:
            stmt = stmt.where(RestoreJob.organization_id == org_id)
        stmt = stmt.order_by(RestoreJob.executed_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ----------------------------------------------------
    # Performance & Load Test Operations
    # ----------------------------------------------------
    async def save_performance_report(
        self, report: PerformanceReport
    ) -> PerformanceReport:
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def list_performance_reports(
        self, limit: int = 50
    ) -> list[PerformanceReport]:
        stmt = (
            select(PerformanceReport)
            .order_by(PerformanceReport.generated_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def save_load_test_result(self, result_obj: LoadTestResult) -> LoadTestResult:
        self.db.add(result_obj)
        await self.db.commit()
        await self.db.refresh(result_obj)
        return result_obj

    async def list_load_test_results(self, limit: int = 50) -> list[LoadTestResult]:
        stmt = (
            select(LoadTestResult).order_by(LoadTestResult.run_at.desc()).limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ----------------------------------------------------
    # Compliance Operations
    # ----------------------------------------------------
    async def save_compliance_report(
        self, report: ComplianceReport
    ) -> ComplianceReport:
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def list_compliance_reports(
        self, framework: str | None = None
    ) -> list[ComplianceReport]:
        stmt = select(ComplianceReport)
        if framework:
            stmt = stmt.where(ComplianceReport.framework == framework)
        stmt = stmt.order_by(ComplianceReport.audited_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
