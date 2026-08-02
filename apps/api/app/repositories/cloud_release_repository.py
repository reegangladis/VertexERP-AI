from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cloud_release import (
    CloudDeploymentHistory,
    CloudRegion,
    CostReport,
    IncidentReport,
    ReleaseHistory,
)


class CloudReleaseRepository:
    """Async SQLAlchemy repository for Cloud Deployments, Releases, FinOps, and Incidents."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ----------------------------------------------------
    # Release History Operations
    # ----------------------------------------------------
    async def create_release(self, release: ReleaseHistory) -> ReleaseHistory:
        self.db.add(release)
        await self.db.commit()
        await self.db.refresh(release)
        return release

    async def list_releases(self, limit: int = 50) -> list[ReleaseHistory]:
        stmt = (
            select(ReleaseHistory)
            .order_by(ReleaseHistory.released_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_release_by_version(self, version: str) -> ReleaseHistory | None:
        stmt = select(ReleaseHistory).where(ReleaseHistory.version == version)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ----------------------------------------------------
    # Deployment History Operations
    # ----------------------------------------------------
    async def create_deployment(
        self, deployment: CloudDeploymentHistory
    ) -> CloudDeploymentHistory:
        self.db.add(deployment)
        await self.db.commit()
        await self.db.refresh(deployment)
        return deployment

    async def list_deployments(
        self, env_name: str | None = None, limit: int = 50
    ) -> list[CloudDeploymentHistory]:
        stmt = select(CloudDeploymentHistory)
        if env_name:
            stmt = stmt.where(CloudDeploymentHistory.environment_name == env_name)
        stmt = stmt.order_by(CloudDeploymentHistory.deployed_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ----------------------------------------------------
    # Cloud Region Operations
    # ----------------------------------------------------
    async def save_region(self, region: CloudRegion) -> CloudRegion:
        self.db.add(region)
        await self.db.commit()
        await self.db.refresh(region)
        return region

    async def list_cloud_regions(self) -> list[CloudRegion]:
        stmt = select(CloudRegion).order_by(CloudRegion.region_code.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ----------------------------------------------------
    # FinOps Cost Operations
    # ----------------------------------------------------
    async def save_cost_report(self, report: CostReport) -> CostReport:
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def list_cost_reports(self, limit: int = 24) -> list[CostReport]:
        stmt = select(CostReport).order_by(CostReport.generated_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ----------------------------------------------------
    # Incident Management Operations
    # ----------------------------------------------------
    async def create_incident(self, incident: IncidentReport) -> IncidentReport:
        self.db.add(incident)
        await self.db.commit()
        await self.db.refresh(incident)
        return incident

    async def list_incidents(
        self, severity: str | None = None, limit: int = 50
    ) -> list[IncidentReport]:
        stmt = select(IncidentReport)
        if severity:
            stmt = stmt.where(IncidentReport.severity == severity)
        stmt = stmt.order_by(IncidentReport.created_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
