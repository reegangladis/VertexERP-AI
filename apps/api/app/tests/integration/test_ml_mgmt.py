import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.ml import (
    MLModelCreate,
    MLPredictionRequest,
)
from app.services.ml.inference_service import InferenceService
from app.services.ml.registry_service import ModelRegistryService
from app.services.ml.training_service import TrainingService


@pytest.mark.asyncio
async def test_model_registry_integration_flow():
    db_mock = AsyncMock()
    service = ModelRegistryService(db_mock)
    org_id = uuid.uuid4()
    model_id = uuid.uuid4()
    version_id = uuid.uuid4()

    mock_model = MagicMock()
    mock_model.id = model_id
    mock_model.model_code = "HR_ATTRITION_V1"

    mock_version = MagicMock()
    mock_version.id = version_id
    mock_version.status = "PRODUCTION"
    mock_version.approval_status = "APPROVED"

    service.repo.create_model = AsyncMock(return_value=mock_model)
    service.repo.create_model_version = AsyncMock(return_value=mock_version)
    service.repo.update_version_status = AsyncMock(return_value=mock_version)

    model = await service.register_model(
        org_id,
        MLModelCreate(
            model_code="HR_ATTRITION_V1",
            name="HR Attrition Model",
            model_type="CLASSIFICATION",
            ml_framework="XGBOOST",
            business_domain="HR",
        ),
    )
    assert model.model_code == "HR_ATTRITION_V1"

    approved = await service.approve_model_version(
        version_id, MagicMock(approved_by="Lead ML Engineer")
    )
    assert approved.approval_status == "APPROVED"


@pytest.mark.asyncio
async def test_training_job_execution_flow():
    db_mock = AsyncMock()
    service = TrainingService(db_mock)
    org_id = uuid.uuid4()
    job_id = uuid.uuid4()

    mock_job = MagicMock()
    mock_job.id = job_id
    mock_job.model_type = "CLASSIFICATION"
    mock_job.ml_framework = "XGBOOST"
    mock_job.hyperparameters_json = {"n_estimators": 50}
    mock_job.runs = []
    mock_job.model_id = None

    service.repo.get_training_job_by_id = AsyncMock(return_value=mock_job)
    service.repo.create_training_run = AsyncMock()

    executed_job = await service.execute_training_job(job_id)
    assert executed_job.status == "COMPLETED"


@pytest.mark.asyncio
async def test_inference_service_predict_flow():
    db_mock = AsyncMock()
    service = InferenceService(db_mock)
    org_id = uuid.uuid4()

    mock_pred = MagicMock()
    mock_pred.status = "SUCCESS"
    mock_pred.confidence_score = 0.96

    service.repo.create_prediction = AsyncMock(return_value=mock_pred)

    pred = await service.predict_realtime(
        org_id,
        MLPredictionRequest(
            business_module="attrition",
            input_data={"tenure": 12, "overtime": 20},
        ),
    )
    assert pred.status == "SUCCESS"
    assert pred.confidence_score > 0.90
