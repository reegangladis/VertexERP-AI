import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# --- Dataset & Pipeline Schemas ---
class DatasetBase(BaseModel):
    dataset_name: str = Field(..., min_length=1, max_length=255)
    dataset_type: str = Field(default="Tabular", max_length=50)
    source: str = Field(..., min_length=1, max_length=255)
    schema_version: str = Field(default="v1.0", max_length=50)
    status: str = Field(default="Active", max_length=50)


class DatasetCreate(DatasetBase):
    organization_id: uuid.UUID


class DatasetResponse(DatasetBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PipelineJobBase(BaseModel):
    pipeline_name: str = Field(..., min_length=1, max_length=255)
    schedule_cron: str | None = Field(None, max_length=100)
    status: str = Field(default="Active", max_length=50)


class PipelineJobCreate(PipelineJobBase):
    organization_id: uuid.UUID


class PipelineJobResponse(PipelineJobBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ETLJobBase(BaseModel):
    job_name: str = Field(..., min_length=1, max_length=255)
    source_type: str = Field(..., min_length=1, max_length=100)
    target_type: str = Field(..., min_length=1, max_length=100)
    status: str = Field(default="Idle", max_length=50)


class ETLJobCreate(ETLJobBase):
    pass


class ETLJobResponse(ETLJobBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Feature Store Schemas ---
class FeatureStoreBase(BaseModel):
    feature_name: str = Field(..., min_length=1, max_length=255)
    feature_group: str = Field(..., min_length=1, max_length=100)
    data_type: str = Field(default="FLOAT", max_length=50)
    description: str | None = Field(None, max_length=1000)
    version: str = Field(default="v1.0", max_length=50)
    status: str = Field(default="Active", max_length=50)


class FeatureStoreCreate(FeatureStoreBase):
    feature_group_id: uuid.UUID | None = None


class FeatureStoreResponse(FeatureStoreBase):
    id: uuid.UUID
    feature_group_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- ML Models & Registry Schemas ---
class MLModelBase(BaseModel):
    model_name: str = Field(..., min_length=1, max_length=255)
    algorithm: str = Field(..., min_length=1, max_length=100)
    framework: str = Field(default="scikit-learn", max_length=50)
    problem_type: str = Field(default="Classification", max_length=50)
    current_version: str = Field(default="v1.0.0", max_length=50)
    status: str = Field(default="Production", max_length=50)


class MLModelCreate(MLModelBase):
    organization_id: uuid.UUID


class MLModelResponse(MLModelBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ModelVersionCreate(BaseModel):
    model_id: uuid.UUID
    version: str = Field(..., min_length=1, max_length=50)
    metrics: str = Field(..., min_length=1)  # JSON string
    artifact_path: str = Field(..., min_length=1, max_length=500)


class ModelVersionResponse(BaseModel):
    id: uuid.UUID
    model_id: uuid.UUID
    version: str
    metrics: str
    artifact_path: str
    registered_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Training & Predictions Schemas ---
class TrainingJobCreate(BaseModel):
    model_id: uuid.UUID
    dataset_id: uuid.UUID


class TrainingJobResponse(BaseModel):
    id: uuid.UUID
    model_id: uuid.UUID
    dataset_id: uuid.UUID
    started_at: datetime
    completed_at: datetime | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PredictionRequest(BaseModel):
    model_version_id: uuid.UUID
    input_data: dict = Field(...)


class PredictionResult(BaseModel):
    prediction_id: uuid.UUID
    model_version_id: uuid.UUID
    prediction_output: dict
    latency_sec: float
    confidence_score: float
    status: str


# --- Drift Monitoring Schemas ---
class DriftReportCreate(BaseModel):
    model_id: uuid.UUID
    drift_type: str = Field(default="Data Drift", max_length=50)


class DriftReportResponse(BaseModel):
    id: uuid.UUID
    model_id: uuid.UUID
    drift_type: str
    drift_score: float
    threshold: float
    status: str
    generated_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Dashboard Summary Schema ---
class DataPlatformDashboardSummary(BaseModel):
    total_datasets: int
    total_pipeline_runs: int
    total_features_in_store: int
    active_ml_models: int
    total_predictions: int
    active_drift_alerts: int
    average_prediction_latency_ms: float
    training_jobs_completed: int
