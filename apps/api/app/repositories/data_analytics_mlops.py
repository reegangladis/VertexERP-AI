import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.data_analytics_mlops_v15 import (
    Dataset,
    DatasetVersion,
    DriftReport,
    ETLJob,
    Experiment,
    FeatureGroup,
    FeatureStore,
    MLModel,
    ModelVersion,
    PipelineJob,
    PredictionHistory,
    TrainingJob,
)
from app.repositories.base import BaseRepository


class DatasetRepository(BaseRepository[Dataset]):
    def __init__(self, db: AsyncSession):
        super().__init__(Dataset, db)

    async def find_by_name(self, org_id: uuid.UUID, name: str) -> Dataset | None:
        stmt = select(Dataset).where(
            Dataset.organization_id == org_id, Dataset.dataset_name == name, Dataset.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_org(self, org_id: uuid.UUID) -> list[Dataset]:
        stmt = select(Dataset).where(
            Dataset.organization_id == org_id, Dataset.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class PipelineJobRepository(BaseRepository[PipelineJob]):
    def __init__(self, db: AsyncSession):
        super().__init__(PipelineJob, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[PipelineJob]:
        stmt = select(PipelineJob).where(
            PipelineJob.organization_id == org_id, PipelineJob.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class ETLJobRepository(BaseRepository[ETLJob]):
    def __init__(self, db: AsyncSession):
        super().__init__(ETLJob, db)

    async def find_by_name(self, name: str) -> ETLJob | None:
        stmt = select(ETLJob).where(
            ETLJob.job_name == name, ETLJob.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class FeatureStoreRepository(BaseRepository[FeatureStore]):
    def __init__(self, db: AsyncSession):
        super().__init__(FeatureStore, db)

    async def find_by_name(self, name: str) -> FeatureStore | None:
        stmt = select(FeatureStore).where(
            FeatureStore.feature_name == name, FeatureStore.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class MLModelRepository(BaseRepository[MLModel]):
    def __init__(self, db: AsyncSession):
        super().__init__(MLModel, db)

    async def find_by_name(self, org_id: uuid.UUID, name: str) -> MLModel | None:
        stmt = select(MLModel).where(
            MLModel.organization_id == org_id, MLModel.model_name == name, MLModel.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_org(self, org_id: uuid.UUID) -> list[MLModel]:
        stmt = select(MLModel).where(
            MLModel.organization_id == org_id, MLModel.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class ModelVersionRepository(BaseRepository[ModelVersion]):
    def __init__(self, db: AsyncSession):
        super().__init__(ModelVersion, db)


class TrainingJobRepository(BaseRepository[TrainingJob]):
    def __init__(self, db: AsyncSession):
        super().__init__(TrainingJob, db)


class PredictionHistoryRepository(BaseRepository[PredictionHistory]):
    def __init__(self, db: AsyncSession):
        super().__init__(PredictionHistory, db)


class DriftReportRepository(BaseRepository[DriftReport]):
    def __init__(self, db: AsyncSession):
        super().__init__(DriftReport, db)
