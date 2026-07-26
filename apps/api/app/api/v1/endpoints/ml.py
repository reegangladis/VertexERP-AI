import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.models.user import User
from app.core.dependencies import get_current_user


from app.schemas.ml import (
    MLModelCreate,
    MLModelResponse,
    MLModelUpdate,
    ModelVersionCreate,
    ModelVersionResponse,
    ModelVersionApprove,
    MLTrainingJobCreate,
    MLTrainingJobResponse,
    MLPredictionRequest,
    MLBatchPredictionRequest,
    MLPredictionResponse,
    MLPredictionFeedback,
    MLExperimentCreate,
    MLExperimentResponse,
    MLExperimentRunCreate,
    MLExperimentRunResponse,
    MLEvaluationMetricResponse,
    MLFeatureMetadataCreate,
    MLFeatureMetadataResponse,
    BusinessModulePredictRequest,
    BusinessModulePredictResponse,
)

from app.services.ml.registry_service import ModelRegistryService
from app.services.ml.training_service import TrainingService
from app.services.ml.experiment_service import ExperimentService
from app.services.ml.inference_service import InferenceService
from app.services.ml.evaluation_service import EvaluationService
from app.services.ml.business_modules import BusinessMLModulesService
from app.services.ml.dataset_service import MLDatasetGenerator
from app.repositories.ml_repository import MLRepository

router = APIRouter()


# =============================================================================
# MODEL REGISTRY ENDPOINTS
# =============================================================================
@router.post("/models", response_model=MLModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    payload: MLModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Registers a new Machine Learning Model in the Enterprise Model Registry."""
    service = ModelRegistryService(db)
    return await service.register_model(current_user.organization_id, payload)


@router.get("/models", response_model=List[MLModelResponse])
async def list_models(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists registered Machine Learning Models and their version histories."""
    service = ModelRegistryService(db)
    return await service.get_registered_models(current_user.organization_id)


@router.get("/models/{model_id}", response_model=MLModelResponse)
async def get_model(
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetches model details and versions by Model ID."""
    service = ModelRegistryService(db)
    model_obj = await service.get_model_by_id(model_id)
    if not model_obj:
        raise HTTPException(status_code=404, detail="Model not found")
    return model_obj


@router.post("/models/{model_id}/versions", response_model=ModelVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_model_version(
    model_id: uuid.UUID,
    payload: ModelVersionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Creates a candidate version for a registered model."""
    service = ModelRegistryService(db)
    return await service.create_model_version(model_id, payload)


@router.post("/versions/{version_id}/approve", response_model=ModelVersionResponse)
async def approve_model_version(
    version_id: uuid.UUID,
    payload: ModelVersionApprove,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approves a candidate model version and promotes it to PRODUCTION."""
    service = ModelRegistryService(db)
    approved_ver = await service.approve_model_version(version_id, payload)
    if not approved_ver:
        raise HTTPException(status_code=404, detail="Model version not found")
    return approved_ver


# =============================================================================
# TRAINING JOBS ENDPOINTS
# =============================================================================
@router.post("/training-jobs", response_model=MLTrainingJobResponse, status_code=status.HTTP_201_CREATED)
async def create_training_job(
    payload: MLTrainingJobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Creates a new model training job configuration."""
    service = TrainingService(db)
    return await service.create_training_job(current_user.organization_id, payload)


@router.get("/training-jobs", response_model=List[MLTrainingJobResponse])
async def list_training_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists training job executions and run logs."""
    service = TrainingService(db)
    return await service.get_training_jobs(current_user.organization_id)


@router.post("/training-jobs/{job_id}/execute", response_model=MLTrainingJobResponse)
async def execute_training_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Triggers execution for a pending ML training job."""
    service = TrainingService(db)
    try:
        return await service.execute_training_job(job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# =============================================================================
# INFERENCE & PREDICTIONS ENDPOINTS
# =============================================================================
@router.post("/inference/predict", response_model=MLPredictionResponse)
async def predict_realtime(
    payload: MLPredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Executes single real-time prediction inference request."""
    service = InferenceService(db)
    return await service.predict_realtime(current_user.organization_id, payload)


@router.post("/inference/predict-batch", response_model=List[MLPredictionResponse])
async def predict_batch(
    payload: MLBatchPredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Executes batch inference prediction request for multiple items."""
    service = InferenceService(db)
    return await service.predict_batch(current_user.organization_id, payload)


@router.get("/inference/history", response_model=List[MLPredictionResponse])
async def get_prediction_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists recent prediction history and latency metadata."""
    service = InferenceService(db)
    return await service.get_prediction_history(current_user.organization_id)


@router.post("/inference/feedback")
async def submit_prediction_feedback(
    payload: MLPredictionFeedback,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Logs ground truth evaluation feedback for prediction history quality auditing."""
    service = InferenceService(db)
    return await service.submit_prediction_feedback(payload)


# =============================================================================
# EXPERIMENT REGISTRY ENDPOINTS
# =============================================================================
@router.post("/experiments", response_model=MLExperimentResponse, status_code=status.HTTP_201_CREATED)
async def create_experiment(
    payload: MLExperimentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Registers a new ML Experiment for tracking hyperparameter exploration."""
    service = ExperimentService(db)
    return await service.create_experiment(current_user.organization_id, payload)


@router.get("/experiments", response_model=List[MLExperimentResponse])
async def list_experiments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists registered ML Experiments and trial runs."""
    service = ExperimentService(db)
    return await service.get_experiments(current_user.organization_id)


@router.post("/experiments/{experiment_id}/runs", response_model=MLExperimentRunResponse)
async def create_experiment_run(
    experiment_id: uuid.UUID,
    payload: MLExperimentRunCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Logs an iteration run under an experiment."""
    service = ExperimentService(db)
    return await service.create_experiment_run(experiment_id, payload)


# =============================================================================
# BUSINESS ML MODULES ENDPOINTS
# =============================================================================
@router.post("/business-modules/predict", response_model=BusinessModulePredictResponse)
async def predict_business_module(
    payload: BusinessModulePredictRequest,
    current_user: User = Depends(get_current_user),
):
    """Executes domain-specific prediction engine for HR Attrition, Sales, Demand, Inventory, Churn, Fraud, Quality, Maintenance, and Revenue."""
    key = payload.module_key.lower()
    data = payload.input_data

    if key in ["attrition", "employee_attrition"]:
        return BusinessMLModulesService.predict_attrition(data)
    elif key in ["sales", "sales_forecasting"]:
        return BusinessMLModulesService.predict_sales_forecast(data)
    elif key in ["demand", "demand_forecasting"]:
        return BusinessMLModulesService.predict_demand_forecast(data)
    elif key in ["inventory", "inventory_opt"]:
        return BusinessMLModulesService.predict_inventory_optimization(data)
    elif key in ["churn", "customer_churn"]:
        return BusinessMLModulesService.predict_customer_churn(data)
    elif key in ["fraud", "fraud_detection"]:
        return BusinessMLModulesService.predict_fraud(data)
    elif key in ["quality", "quality_prediction"]:
        return BusinessMLModulesService.predict_quality(data)
    elif key in ["maintenance", "predictive_maintenance"]:
        return BusinessMLModulesService.predict_maintenance(data)
    elif key in ["revenue", "revenue_forecasting"]:
        return BusinessMLModulesService.predict_revenue_forecast(data)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported business module key '{key}'")


# =============================================================================
# FEATURE METADATA & METRICS ENDPOINTS
# =============================================================================
@router.post("/feature-metadata", response_model=MLFeatureMetadataResponse, status_code=status.HTTP_201_CREATED)
async def create_feature_metadata(
    payload: MLFeatureMetadataCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Registers feature preprocessing and transformer metadata."""
    repo = MLRepository(db)
    feat_obj = MLFeatureMetadata(
        organization_id=current_user.organization_id,
        feature_name=payload.feature_name,
        feature_type=payload.feature_type,
        data_type=payload.data_type,
        pipeline_stage=payload.pipeline_stage,
        transformer_type=payload.transformer_type,
        scaling_type=payload.scaling_type,
        missing_handler=payload.missing_handler,
        outlier_handler=payload.outlier_handler,
        metadata_json=payload.metadata_json or {},
    )
    return await repo.create_feature_metadata(feat_obj)


@router.get("/feature-metadata", response_model=List[MLFeatureMetadataResponse])
async def list_feature_metadata(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists registered ML feature metadata."""
    repo = MLRepository(db)
    return await repo.get_feature_metadata_list(current_user.organization_id)


@router.post("/datasets/generate-root-files")
async def generate_root_datasets(
    current_user: User = Depends(get_current_user),
):
    """Exports seed ML datasets to the root datasets/ directory."""
    files = MLDatasetGenerator.export_all_datasets_to_root()
    return {"status": "SUCCESS", "generated_files": files}

