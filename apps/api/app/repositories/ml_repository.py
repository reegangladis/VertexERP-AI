import uuid
from datetime import datetime

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ml import (
    MLEvaluationMetric,
    MLExperiment,
    MLExperimentRun,
    MLFeatureMetadata,
    MLModel,
    MLPrediction,
    MLPredictionHistory,
    MLTrainingJob,
    MLTrainingRun,
    ModelVersion,
)


class MLRepository:
    """Repository handling all Machine Learning Platform database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================================================================
    # ML MODELS & VERSIONS
    # =========================================================================
    async def create_model(self, model: MLModel) -> MLModel:
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model

    async def get_models(self, organization_id: uuid.UUID) -> list[MLModel]:
        stmt = (
            select(MLModel)
            .options(selectinload(MLModel.versions))
            .where(MLModel.organization_id == organization_id)
            .order_by(desc(MLModel.created_at))
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_model_by_id(self, model_id: uuid.UUID) -> MLModel | None:
        stmt = (
            select(MLModel)
            .options(selectinload(MLModel.versions))
            .where(MLModel.id == model_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_model_by_code(
        self, organization_id: uuid.UUID, model_code: str
    ) -> MLModel | None:
        stmt = (
            select(MLModel)
            .options(selectinload(MLModel.versions))
            .where(
                MLModel.organization_id == organization_id,
                MLModel.model_code == model_code,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create_model_version(self, version: ModelVersion) -> ModelVersion:
        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)
        return version

    async def get_model_version_by_id(
        self, version_id: uuid.UUID
    ) -> ModelVersion | None:
        stmt = select(ModelVersion).where(ModelVersion.id == version_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def update_version_status(
        self,
        version_id: uuid.UUID,
        status: str,
        approval_status: str,
        approved_by: str | None = None,
    ) -> ModelVersion | None:
        stmt = (
            update(ModelVersion)
            .where(ModelVersion.id == version_id)
            .values(
                status=status,
                approval_status=approval_status,
                approved_by=approved_by,
                approved_at=(
                    datetime.utcnow() if approval_status == "APPROVED" else None
                ),
            )
            .returning(ModelVersion)
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.scalar_one_or_none()

    # =========================================================================
    # TRAINING JOBS & RUNS
    # =========================================================================
    async def create_training_job(self, job: MLTrainingJob) -> MLTrainingJob:
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get_training_jobs(
        self, organization_id: uuid.UUID
    ) -> list[MLTrainingJob]:
        stmt = (
            select(MLTrainingJob)
            .options(selectinload(MLTrainingJob.runs))
            .where(MLTrainingJob.organization_id == organization_id)
            .order_by(desc(MLTrainingJob.created_at))
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_training_job_by_id(self, job_id: uuid.UUID) -> MLTrainingJob | None:
        stmt = (
            select(MLTrainingJob)
            .options(selectinload(MLTrainingJob.runs))
            .where(MLTrainingJob.id == job_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create_training_run(self, run: MLTrainingRun) -> MLTrainingRun:
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    # =========================================================================
    # PREDICTIONS & INFERENCE HISTORY
    # =========================================================================
    async def create_prediction(self, prediction: MLPrediction) -> MLPrediction:
        self.db.add(prediction)
        await self.db.commit()
        await self.db.refresh(prediction)
        return prediction

    async def get_predictions(
        self, organization_id: uuid.UUID, limit: int = 100
    ) -> list[MLPrediction]:
        stmt = (
            select(MLPrediction)
            .where(MLPrediction.organization_id == organization_id)
            .order_by(desc(MLPrediction.created_at))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def create_prediction_history(
        self, history: MLPredictionHistory
    ) -> MLPredictionHistory:
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    # =========================================================================
    # EXPERIMENTS & EXPERIMENT RUNS
    # =========================================================================
    async def create_experiment(self, experiment: MLExperiment) -> MLExperiment:
        self.db.add(experiment)
        await self.db.commit()
        await self.db.refresh(experiment)
        return experiment

    async def get_experiments(self, organization_id: uuid.UUID) -> list[MLExperiment]:
        stmt = (
            select(MLExperiment)
            .options(selectinload(MLExperiment.runs))
            .where(MLExperiment.organization_id == organization_id)
            .order_by(desc(MLExperiment.created_at))
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_experiment_by_id(
        self, experiment_id: uuid.UUID
    ) -> MLExperiment | None:
        stmt = (
            select(MLExperiment)
            .options(selectinload(MLExperiment.runs))
            .where(MLExperiment.id == experiment_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create_experiment_run(self, run: MLExperimentRun) -> MLExperimentRun:
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    # =========================================================================
    # EVALUATION METRICS & FEATURE METADATA
    # =========================================================================
    async def create_evaluation_metric(
        self, metric: MLEvaluationMetric
    ) -> MLEvaluationMetric:
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        return metric

    async def get_metrics_by_version(
        self, model_version_id: uuid.UUID
    ) -> list[MLEvaluationMetric]:
        stmt = (
            select(MLEvaluationMetric)
            .where(MLEvaluationMetric.model_version_id == model_version_id)
            .order_by(MLEvaluationMetric.metric_name)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def create_feature_metadata(
        self, metadata: MLFeatureMetadata
    ) -> MLFeatureMetadata:
        self.db.add(metadata)
        await self.db.commit()
        await self.db.refresh(metadata)
        return metadata

    async def get_feature_metadata_list(
        self, organization_id: uuid.UUID
    ) -> list[MLFeatureMetadata]:
        stmt = (
            select(MLFeatureMetadata)
            .where(MLFeatureMetadata.organization_id == organization_id)
            .order_by(MLFeatureMetadata.feature_name)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
