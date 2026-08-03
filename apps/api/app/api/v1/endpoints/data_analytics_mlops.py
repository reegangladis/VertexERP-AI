import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_db_session
from app.models.user import User
from app.repositories.data_analytics_mlops import (
    DatasetRepository,
    ETLJobRepository,
    FeatureStoreRepository,
    MLModelRepository,
    PipelineJobRepository,
)
from app.schemas.data_analytics_mlops import (
    DataPlatformDashboardSummary,
    DatasetCreate,
    DatasetResponse,
    DriftReportCreate,
    DriftReportResponse,
    ETLJobCreate,
    ETLJobResponse,
    FeatureStoreCreate,
    FeatureStoreResponse,
    MLModelCreate,
    MLModelResponse,
    ModelVersionCreate,
    ModelVersionResponse,
    PipelineJobCreate,
    PipelineJobResponse,
    PredictionRequest,
    PredictionResult,
    TrainingJobCreate,
    TrainingJobResponse,
)
from app.services.data_analytics_mlops import (
    DataPlatformAnalyticsService,
    DatasetETLService,
    DriftMonitoringEngine,
    FeatureStoreEngine,
    MLOpsEngine,
    PredictionEngine,
)

router = APIRouter()


# --- Datasets ---
@router.post("/analytics/datasets", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    payload: DatasetCreate,
    current_user: User = Depends(PermissionChecker("dataset.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = DatasetETLService(db)
    return await service.create_dataset(payload)


@router.get("/analytics/datasets", response_model=list[DatasetResponse])
async def list_datasets(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("analytics.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = DatasetRepository(db)
    return await repo.get_by_org(org_id)


# --- Pipelines & ETL ---
@router.post("/analytics/pipelines", response_model=PipelineJobResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline(
    payload: PipelineJobCreate,
    current_user: User = Depends(PermissionChecker("analytics.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = DatasetETLService(db)
    return await service.create_pipeline_job(payload)


@router.get("/analytics/pipelines", response_model=list[PipelineJobResponse])
async def list_pipelines(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("analytics.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = PipelineJobRepository(db)
    return await repo.get_by_org(org_id)


@router.post("/analytics/etl-jobs", response_model=ETLJobResponse, status_code=status.HTTP_201_CREATED)
async def create_etl_job(
    payload: ETLJobCreate,
    current_user: User = Depends(PermissionChecker("analytics.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = DatasetETLService(db)
    return await service.create_etl_job(payload)


@router.get("/analytics/etl-jobs", response_model=list[ETLJobResponse])
async def list_etl_jobs(
    current_user: User = Depends(PermissionChecker("analytics.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = ETLJobRepository(db)
    records, _ = await repo.get_multi()
    return records


# --- Feature Store ---
@router.post("/analytics/features", response_model=FeatureStoreResponse, status_code=status.HTTP_201_CREATED)
async def create_feature(
    payload: FeatureStoreCreate,
    current_user: User = Depends(PermissionChecker("feature.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = FeatureStoreEngine(db)
    return await engine.create_feature(payload)


@router.get("/analytics/features", response_model=list[FeatureStoreResponse])
async def list_features(
    current_user: User = Depends(PermissionChecker("analytics.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = FeatureStoreRepository(db)
    records, _ = await repo.get_multi()
    return records


# --- MLOps & Model Registry ---
@router.post("/analytics/models", response_model=MLModelResponse, status_code=status.HTTP_201_CREATED)
async def register_ml_model(
    payload: MLModelCreate,
    current_user: User = Depends(PermissionChecker("ml.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = MLOpsEngine(db)
    return await engine.register_model(payload)


@router.get("/analytics/models", response_model=list[MLModelResponse])
async def list_ml_models(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("analytics.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = MLModelRepository(db)
    return await repo.get_by_org(org_id)


@router.post("/analytics/models/versions", response_model=ModelVersionResponse, status_code=status.HTTP_201_CREATED)
async def register_model_version(
    payload: ModelVersionCreate,
    current_user: User = Depends(PermissionChecker("ml.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = MLOpsEngine(db)
    return await engine.register_version(payload)


# --- Training & Predictions ---
@router.post("/analytics/training-jobs", response_model=TrainingJobResponse, status_code=status.HTTP_201_CREATED)
async def create_training_job(
    payload: TrainingJobCreate,
    current_user: User = Depends(PermissionChecker("training.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = MLOpsEngine(db)
    return await engine.create_training_job(payload)


@router.post("/analytics/predictions/online", response_model=PredictionResult)
async def run_online_prediction(
    payload: PredictionRequest,
    current_user: User = Depends(PermissionChecker("prediction.run")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = PredictionEngine(db)
    return await engine.run_online_prediction(payload)


# --- Drift Monitoring ---
@router.post("/analytics/drift/reports", response_model=DriftReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_drift_report(
    payload: DriftReportCreate,
    current_user: User = Depends(PermissionChecker("ml.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = DriftMonitoringEngine(db)
    return await engine.generate_drift_report(payload)


# --- Analytics Dashboard ---
@router.get("/analytics/dashboard", response_model=DataPlatformDashboardSummary)
async def get_analytics_dashboard(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("dashboard.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = DataPlatformAnalyticsService(db)
    return await service.get_dashboard_summary(org_id)
