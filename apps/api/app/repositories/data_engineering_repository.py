import uuid
from typing import Any

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.data_engineering import (
    DataLakeObject,
    DataLineage,
    DataQualityReport,
    Dataset,
    DatasetVersion,
    ETLJob,
    ETLRun,
    FeatureGroup,
    FeatureRegistry,
    MDMGoldenRecord,
    MetadataCatalog,
    PipelineLog,
)


class DataEngineeringRepository:
    """Repository handling all Data Engineering, Data Warehouse, Lake, and Feature Store operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================================================================
    # ETL JOBS & RUNS
    # =========================================================================
    async def create_job(self, job: ETLJob) -> ETLJob:
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get_jobs_by_org(self, organization_id: uuid.UUID) -> list[ETLJob]:
        stmt = (
            select(ETLJob)
            .where(ETLJob.organization_id == organization_id)
            .order_by(ETLJob.name)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_job_by_id(self, job_id: uuid.UUID) -> ETLJob | None:
        stmt = (
            select(ETLJob).options(selectinload(ETLJob.runs)).where(ETLJob.id == job_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create_run(self, run: ETLRun) -> ETLRun:
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def update_run(
        self, run_id: uuid.UUID, updates: dict[str, Any]
    ) -> ETLRun | None:
        stmt = (
            update(ETLRun)
            .where(ETLRun.id == run_id)
            .values(**updates)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(stmt)
        await self.db.commit()

        stmt_fetch = select(ETLRun).where(ETLRun.id == run_id)
        res = await self.db.execute(stmt_fetch)
        return res.scalar_one_or_none()

    async def get_runs_by_job(self, job_id: uuid.UUID, limit: int = 50) -> list[ETLRun]:
        stmt = (
            select(ETLRun)
            .where(ETLRun.job_id == job_id)
            .order_by(desc(ETLRun.start_time))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def add_pipeline_log(self, log: PipelineLog) -> PipelineLog:
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_run_logs(self, run_id: uuid.UUID) -> list[PipelineLog]:
        stmt = (
            select(PipelineLog)
            .where(PipelineLog.run_id == run_id)
            .order_by(PipelineLog.timestamp)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # =========================================================================
    # DATASETS & CATALOG
    # =========================================================================
    async def create_dataset(self, dataset: Dataset) -> Dataset:
        self.db.add(dataset)
        await self.db.commit()
        await self.db.refresh(dataset)
        return dataset

    async def get_datasets_by_org(self, organization_id: uuid.UUID) -> list[Dataset]:
        stmt = (
            select(Dataset)
            .where(Dataset.organization_id == organization_id)
            .order_by(Dataset.name)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_dataset_by_id(self, dataset_id: uuid.UUID) -> Dataset | None:
        stmt = (
            select(Dataset)
            .options(
                selectinload(Dataset.versions), selectinload(Dataset.metadata_columns)
            )
            .where(Dataset.id == dataset_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create_dataset_version(self, version: DatasetVersion) -> DatasetVersion:
        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)
        return version

    async def add_metadata_catalog_entry(
        self, entry: MetadataCatalog
    ) -> MetadataCatalog:
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def get_metadata_catalog(
        self, dataset_id: uuid.UUID | None = None
    ) -> list[MetadataCatalog]:
        stmt = select(MetadataCatalog)
        if dataset_id:
            stmt = stmt.where(MetadataCatalog.dataset_id == dataset_id)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # =========================================================================
    # FEATURE STORE
    # =========================================================================
    async def create_feature_group(self, group: FeatureGroup) -> FeatureGroup:
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def get_feature_groups_by_org(
        self, organization_id: uuid.UUID
    ) -> list[FeatureGroup]:
        stmt = (
            select(FeatureGroup)
            .options(selectinload(FeatureGroup.features))
            .where(FeatureGroup.organization_id == organization_id)
            .order_by(FeatureGroup.group_name)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def create_feature(self, feature: FeatureRegistry) -> FeatureRegistry:
        self.db.add(feature)
        await self.db.commit()
        await self.db.refresh(feature)
        return feature

    # =========================================================================
    # DATA QUALITY
    # =========================================================================
    async def create_quality_report(
        self, report: DataQualityReport
    ) -> DataQualityReport:
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_quality_reports_by_org(
        self, organization_id: uuid.UUID, limit: int = 50
    ) -> list[DataQualityReport]:
        stmt = (
            select(DataQualityReport)
            .where(DataQualityReport.organization_id == organization_id)
            .order_by(desc(DataQualityReport.created_at))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # =========================================================================
    # LINEAGE
    # =========================================================================
    async def create_lineage_edge(self, edge: DataLineage) -> DataLineage:
        self.db.add(edge)
        await self.db.commit()
        await self.db.refresh(edge)
        return edge

    async def get_lineage_graph(self, organization_id: uuid.UUID) -> list[DataLineage]:
        stmt = select(DataLineage).where(DataLineage.organization_id == organization_id)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # =========================================================================
    # DATA LAKE & MDM
    # =========================================================================
    async def get_data_lake_objects(
        self, organization_id: uuid.UUID, zone: str | None = None
    ) -> list[DataLakeObject]:
        stmt = select(DataLakeObject).where(
            DataLakeObject.organization_id == organization_id
        )
        if zone:
            stmt = stmt.where(DataLakeObject.zone == zone)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def create_data_lake_object(self, obj: DataLakeObject) -> DataLakeObject:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get_mdm_golden_records(
        self, organization_id: uuid.UUID, entity_type: str | None = None
    ) -> list[MDMGoldenRecord]:
        stmt = select(MDMGoldenRecord).where(
            MDMGoldenRecord.organization_id == organization_id
        )
        if entity_type:
            stmt = stmt.where(MDMGoldenRecord.entity_type == entity_type)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def create_mdm_record(self, record: MDMGoldenRecord) -> MDMGoldenRecord:
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record
