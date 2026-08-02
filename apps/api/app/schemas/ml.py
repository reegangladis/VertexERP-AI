import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ML Model Schemas
class MLModelCreate(BaseModel):
    model_code: str = Field(..., max_length=100)
    name: str = Field(..., max_length=150)
    description: str | None = None
    model_type: str = Field(
        ...,
        description="CLASSIFICATION, REGRESSION, CLUSTERING, TIME_SERIES, RECOMMENDATION, ANOMALY_DETECTION",
    )
    ml_framework: str = Field(
        ...,
        description="SCIKIT_LEARN, XGBOOST, LIGHTGBM, CATBOOST, TENSORFLOW, PYTORCH, PROPHET",
    )
    business_domain: str = Field(
        ...,
        description="HR, CRM, INVENTORY, FINANCE, MANUFACTURING, SALES, CUSTOMERS, SUPPLIERS",
    )
    target_column: str | None = None
    feature_names: list[str] = Field(default_factory=list)
    metadata_json: dict[str, Any] | None = None


class MLModelUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    feature_names: list[str] | None = None
    metadata_json: dict[str, Any] | None = None


class ModelVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    model_id: uuid.UUID
    version: str
    status: str
    hyperparameters: dict[str, Any] | None
    metrics_json: dict[str, Any] | None
    artifact_path: str | None
    approval_status: str
    approved_by: str | None
    approved_at: datetime | None
    created_at: datetime


class MLModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    model_code: str
    name: str
    description: str | None
    model_type: str
    ml_framework: str
    business_domain: str
    target_column: str | None
    feature_names: list[str]
    status: str
    metadata_json: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
    versions: list[ModelVersionResponse] | None = None


class ModelVersionCreate(BaseModel):
    version: str = Field(..., max_length=50)
    hyperparameters: dict[str, Any] | None = None
    metrics_json: dict[str, Any] | None = None
    artifact_path: str | None = None


class ModelVersionApprove(BaseModel):
    approved_by: str = Field(..., max_length=150)


# Training Job Schemas
class MLTrainingJobCreate(BaseModel):
    job_name: str = Field(..., max_length=150)
    model_id: uuid.UUID | None = None
    model_type: str
    ml_framework: str
    dataset_name: str
    hyperparameters_json: dict[str, Any] | None = None


class MLTrainingRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    run_number: int
    metrics_json: dict[str, Any] | None
    hyperparameters_json: dict[str, Any] | None
    artifact_path: str | None
    execution_time_seconds: float
    status: str
    created_at: datetime


class MLTrainingJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    model_id: uuid.UUID | None
    job_name: str
    model_type: str
    ml_framework: str
    dataset_name: str
    hyperparameters_json: dict[str, Any] | None
    status: str
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    runs: list[MLTrainingRunResponse] | None = None


# Inference Schemas
class MLPredictionRequest(BaseModel):
    model_version_id: uuid.UUID | None = None
    model_code: str | None = None
    business_module: str | None = None
    input_data: dict[str, Any]


class MLBatchPredictionRequest(BaseModel):
    model_version_id: uuid.UUID | None = None
    model_code: str | None = None
    business_module: str | None = None
    batch_input_data: list[dict[str, Any]]


class MLPredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    model_version_id: uuid.UUID | None
    prediction_type: str
    business_module: str | None
    input_data_json: dict[str, Any]
    output_data_json: dict[str, Any]
    confidence_score: float | None
    latency_ms: float
    status: str
    created_at: datetime


class MLPredictionFeedback(BaseModel):
    prediction_id: uuid.UUID
    actual_value: Any
    feedback_score: float = Field(..., ge=0.0, le=1.0)
    evaluation_status: str = Field("CORRECT", description="CORRECT, INCORRECT, DRIFTED")


# Experiment Schemas
class MLExperimentCreate(BaseModel):
    name: str = Field(..., max_length=150)
    description: str | None = None
    model_type: str
    target_column: str | None = None


class MLExperimentRunCreate(BaseModel):
    run_name: str = Field(..., max_length=150)
    parameters_json: dict[str, Any] | None = None
    metrics_json: dict[str, Any] | None = None
    artifacts_metadata_json: dict[str, Any] | None = None
    training_history_json: list[dict[str, Any]] | None = None
    duration_seconds: float = 0.0


class MLExperimentRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    experiment_id: uuid.UUID
    run_name: str
    parameters_json: dict[str, Any] | None
    metrics_json: dict[str, Any] | None
    artifacts_metadata_json: dict[str, Any] | None
    training_history_json: list[dict[str, Any]] | None
    status: str
    duration_seconds: float
    created_at: datetime


class MLExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None
    model_type: str
    target_column: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    runs: list[MLExperimentRunResponse] | None = None


# Evaluation Metrics & Feature Metadata Schemas
class MLEvaluationMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    model_version_id: uuid.UUID
    run_id: uuid.UUID | None
    metric_name: str
    metric_value: float
    dataset_type: str
    metadata_json: dict[str, Any] | None
    confusion_matrix_json: dict[str, Any] | None
    feature_importance_json: dict[str, Any] | None
    created_at: datetime


class MLFeatureMetadataCreate(BaseModel):
    feature_name: str = Field(..., max_length=150)
    feature_type: str = Field(
        ..., description="NUMERICAL, CATEGORICAL, DATETIME, TEXT, BOOLEAN"
    )
    data_type: str = Field(..., description="float64, int64, object, bool, datetime64")
    pipeline_stage: str = "PREPROCESSING"
    transformer_type: str | None = None
    scaling_type: str | None = None
    missing_handler: str | None = None
    outlier_handler: str | None = None
    metadata_json: dict[str, Any] | None = None


class MLFeatureMetadataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    feature_name: str
    feature_type: str
    data_type: str
    pipeline_stage: str
    transformer_type: str | None
    scaling_type: str | None
    missing_handler: str | None
    outlier_handler: str | None
    metadata_json: dict[str, Any] | None
    created_at: datetime


# Business ML Module Schemas
class BusinessModulePredictRequest(BaseModel):
    module_key: str = Field(
        ...,
        description="attrition, sales_forecasting, demand_forecasting, inventory_opt, churn, fraud, quality, maintenance, revenue",
    )
    input_data: dict[str, Any]


class BusinessModulePredictResponse(BaseModel):
    module_key: str
    prediction_result: dict[str, Any]
    confidence_score: float
    risk_level: str | None = "LOW"
    recommendations: list[str] = Field(default_factory=list)
    latency_ms: float
