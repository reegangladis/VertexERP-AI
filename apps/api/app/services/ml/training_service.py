import random
import time
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ml import MLTrainingJob, MLTrainingRun, ModelVersion
from app.repositories.ml_repository import MLRepository
from app.schemas.ml import MLTrainingJobCreate
from app.services.ml.evaluation_service import EvaluationService
from app.services.ml.models import MLModelAdapter


class TrainingService:
    """Service handling ML Training Jobs, Cross Validation, Train/Test Split, and Training Runs."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MLRepository(db)
        self.evaluation_service = EvaluationService(db)

    @staticmethod
    def train_test_split(
        data: list[Any], test_size: float = 0.2, seed: int = 42
    ) -> tuple[list[Any], list[Any]]:
        random.seed(seed)
        shuffled = data.copy()
        random.shuffle(shuffled)
        n_test = int(len(shuffled) * test_size)
        return shuffled[n_test:], shuffled[:n_test]

    @staticmethod
    def k_fold_cross_validation(
        data: list[Any], k: int = 5
    ) -> list[tuple[list[Any], list[Any]]]:
        n = len(data)
        fold_size = n // k
        folds = []
        for i in range(k):
            test = data[i * fold_size : (i + 1) * fold_size]
            train = data[: i * fold_size] + data[(i + 1) * fold_size :]
            folds.append((train, test))
        return folds

    async def create_training_job(
        self, organization_id: uuid.UUID, data: MLTrainingJobCreate
    ) -> MLTrainingJob:
        job = MLTrainingJob(
            organization_id=organization_id,
            model_id=data.model_id,
            job_name=data.job_name,
            model_type=data.model_type,
            ml_framework=data.ml_framework,
            dataset_name=data.dataset_name,
            hyperparameters_json=data.hyperparameters_json
            or {"n_estimators": 100, "learning_rate": 0.05, "max_depth": 6},
            status="PENDING",
        )
        return await self.repo.create_training_job(job)

    async def execute_training_job(self, job_id: uuid.UUID) -> MLTrainingJob:
        job = await self.repo.get_training_job_by_id(job_id)
        if not job:
            raise ValueError("Training job not found")

        job.status = "RUNNING"
        job.started_at = datetime.now(UTC)

        start_time = time.time()
        adapter = MLModelAdapter(
            model_type=job.model_type,
            ml_framework=job.ml_framework,
            hyperparameters=job.hyperparameters_json,
        )

        # Simulated synthetic dataset training for the job
        synthetic_X = [[random.uniform(0, 1) for _ in range(5)] for _ in range(200)]
        synthetic_y = (
            [random.choice([0, 1]) for _ in range(200)]
            if job.model_type == "CLASSIFICATION"
            else [random.uniform(10, 100) for _ in range(200)]
        )

        fit_results = adapter.fit(synthetic_X, synthetic_y)
        exec_time = round(time.time() - start_time, 2)

        # Log training run
        run = MLTrainingRun(
            job_id=job.id,
            run_number=len(job.runs) + 1,
            metrics_json=fit_results,
            hyperparameters_json=job.hyperparameters_json,
            artifact_path=f"s3://vertex-ml-jobs/{job.id}/model_artifact.bin",
            execution_time_seconds=exec_time,
            status="COMPLETED",
        )
        await self.repo.create_training_run(run)

        # If model_id is linked, automatically create a new Model Version Candidate
        if job.model_id:
            version_str = f"v1.{len(job.runs) + 1}.0"
            version_obj = ModelVersion(
                model_id=job.model_id,
                version=version_str,
                status="CANDIDATE",
                hyperparameters=job.hyperparameters_json,
                metrics_json=fit_results,
                artifact_path=f"s3://vertex-ml-registry/{job.model_id}/{version_str}/model.bin",
                approval_status="PENDING",
            )
            created_version = await self.repo.create_model_version(version_obj)

            # Record evaluation metrics for candidate version
            y_pred = [
                res["class"] if isinstance(res, dict) else res
                for res in adapter.predict(synthetic_X)
            ]
            await self.evaluation_service.record_evaluation(
                model_version_id=created_version.id,
                model_type=job.model_type,
                feature_names=["f1", "f2", "f3", "f4", "f5"],
                y_true=synthetic_y,
                y_pred=y_pred,
            )

        job.status = "COMPLETED"
        job.completed_at = datetime.now(UTC)
        await self.db.commit()
        return job

    async def get_training_jobs(
        self, organization_id: uuid.UUID
    ) -> list[MLTrainingJob]:
        return await self.repo.get_training_jobs(organization_id)
