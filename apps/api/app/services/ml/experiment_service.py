import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ml import MLExperiment, MLExperimentRun
from app.repositories.ml_repository import MLRepository
from app.schemas.ml import MLExperimentCreate, MLExperimentRunCreate


class ExperimentService:
    """Service managing ML Experiments, Runs, Hyperparameter tracking, and Artifact Metadata."""

    def __init__(self, db: AsyncSession):
        self.repo = MLRepository(db)

    async def create_experiment(
        self, organization_id: uuid.UUID, data: MLExperimentCreate
    ) -> MLExperiment:
        experiment = MLExperiment(
            organization_id=organization_id,
            name=data.name,
            description=data.description,
            model_type=data.model_type,
            target_column=data.target_column,
            status="ACTIVE",
        )
        return await self.repo.create_experiment(experiment)

    async def get_experiments(self, organization_id: uuid.UUID) -> list[MLExperiment]:
        return await self.repo.get_experiments(organization_id)

    async def get_experiment_by_id(
        self, experiment_id: uuid.UUID
    ) -> MLExperiment | None:
        return await self.repo.get_experiment_by_id(experiment_id)

    async def create_experiment_run(
        self, experiment_id: uuid.UUID, data: MLExperimentRunCreate
    ) -> MLExperimentRun:
        run = MLExperimentRun(
            experiment_id=experiment_id,
            run_name=data.run_name,
            parameters_json=data.parameters_json or {},
            metrics_json=data.metrics_json or {},
            artifacts_metadata_json=data.artifacts_metadata_json or {},
            training_history_json=data.training_history_json or [],
            duration_seconds=data.duration_seconds,
            status="FINISHED",
        )
        return await self.repo.create_experiment_run(run)
