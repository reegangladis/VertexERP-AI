import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ML Model Schemas
class MLModelCreate(BaseModel):
    model_code: str = Field(..., max_length=100)
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    model_type: str = Field(..., description="CLASSIFICATION, REGRESSION, CLUSTERING, TIME_SERIES, RECOMMENDATION, ANOMALY_DETECTION")
    ml_framework: str = Field(..., description="SCIKIT_LEARN, XGBOOST, LIGHTGBM, CATBOOST, TENSORFLOW, PYTORCH, PROPHET")
    business_domain: str = Field(..., description="HR, CRM, INVENTORY, FINANCE, MANUFACTURING, SALES, CUSTOMERS, SUPPLIERS")
    target_column: Optional[str] = None
    feature_names: List[str] = Field(default_factory=list)
    metadata_json: Optional[Dict[str, Any]] = None


class MLModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    feature_names: Optional[List[str]] = None
    metadata_json: Optional[Dict[str, Any]] = None


class ModelVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    model_id: uuid.UUID
    version: str
    status: str
    hyperparameters: Optional[Dict[str, Any]]
    metrics_json: Optional[Dict[str, Any]]
    artifact_path: Optional[str]
    approval_status: str
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime


class MLModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    model_code: str
    name: str
    description: Optional[str]
    model_type: str
    ml_framework: str
    business_domain: str
    target_column: Optional[str]
    feature_names: List[str]
    status: str
    metadata_json: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    versions: Optional[List[ModelVersionResponse]] = None


class ModelVersionCreate(BaseModel):
    version: str = Field(..., max_length=50)
    hyperparameters: Optional[Dict[str, Any]] = None
    metrics_json: Optional[Dict[str, Any]] = None
    artifact_path: Optional[str] = None


class ModelVersionApprove(BaseModel):
    approved_by: str = Field(..., max_length=150)


# Training Job Schemas
class MLTrainingJobCreate(BaseModel):
    job_name: str = Field(..., max_length=150)
    model_id: Optional[uuid.UUID] = None
    model_type: str
    ml_framework: str
    dataset_name: str
    hyperparameters_json: Optional[Dict[str, Any]] = None


class MLTrainingRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    run_number: int
    metrics_json: Optional[Dict[str, Any]]
    hyperparameters_json: Optional[Dict[str, Any]]
    artifact_path: Optional[str]
    execution_time_seconds: float
    status: str
    created_at: datetime


class MLTrainingJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    model_id: Optional[uuid.UUID]
    job_name: str
    model_type: str
    ml_framework: str
    dataset_name: str
    hyperparameters_json: Optional[Dict[str, Any]]
    status: str
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    runs: Optional[List[MLTrainingRunResponse]] = None


# Inference Schemas
class MLPredictionRequest(BaseModel):
    model_version_id: Optional[uuid.UUID] = None
    model_code: Optional[str] = None
    business_module: Optional[str] = None
    input_data: Dict[str, Any]


class MLBatchPredictionRequest(BaseModel):
    model_version_id: Optional[uuid.UUID] = None
    model_code: Optional[str] = None
    business_module: Optional[str] = None
    batch_input_data: List[Dict[str, Any]]


class MLPredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    model_version_id: Optional[uuid.UUID]
    prediction_type: str
    business_module: Optional[str]
    input_data_json: Dict[str, Any]
    output_data_json: Dict[str, Any]
    confidence_score: Optional[float]
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
    description: Optional[str] = None
    model_type: str
    target_column: Optional[str] = None


class MLExperimentRunCreate(BaseModel):
    run_name: str = Field(..., max_length=150)
    parameters_json: Optional[Dict[str, Any]] = None
    metrics_json: Optional[Dict[str, Any]] = None
    artifacts_metadata_json: Optional[Dict[str, Any]] = None
    training_history_json: Optional[List[Dict[str, Any]]] = None
    duration_seconds: float = 0.0


class MLExperimentRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    experiment_id: uuid.UUID
    run_name: str
    parameters_json: Optional[Dict[str, Any]]
    metrics_json: Optional[Dict[str, Any]]
    artifacts_metadata_json: Optional[Dict[str, Any]]
    training_history_json: Optional[List[Dict[str, Any]]]
    status: str
    duration_seconds: float
    created_at: datetime


class MLExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: Optional[str]
    model_type: str
    target_column: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    runs: Optional[List[MLExperimentRunResponse]] = None


# Evaluation Metrics & Feature Metadata Schemas
class MLEvaluationMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    model_version_id: uuid.UUID
    run_id: Optional[uuid.UUID]
    metric_name: str
    metric_value: float
    dataset_type: str
    metadata_json: Optional[Dict[str, Any]]
    confusion_matrix_json: Optional[Dict[str, Any]]
    feature_importance_json: Optional[Dict[str, Any]]
    created_at: datetime


class MLFeatureMetadataCreate(BaseModel):
    feature_name: str = Field(..., max_length=150)
    feature_type: str = Field(..., description="NUMERICAL, CATEGORICAL, DATETIME, TEXT, BOOLEAN")
    data_type: str = Field(..., description="float64, int64, object, bool, datetime64")
    pipeline_stage: str = "PREPROCESSING"
    transformer_type: Optional[str] = None
    scaling_type: Optional[str] = None
    missing_handler: Optional[str] = None
    outlier_handler: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class MLFeatureMetadataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    feature_name: str
    feature_type: str
    data_type: str
    pipeline_stage: str
    transformer_type: Optional[str]
    scaling_type: Optional[str]
    missing_handler: Optional[str]
    outlier_handler: Optional[str]
    metadata_json: Optional[Dict[str, Any]]
    created_at: datetime


# Business ML Module Schemas
class BusinessModulePredictRequest(BaseModel):
    module_key: str = Field(..., description="attrition, sales_forecasting, demand_forecasting, inventory_opt, churn, fraud, quality, maintenance, revenue")
    input_data: Dict[str, Any]


class BusinessModulePredictResponse(BaseModel):
    module_key: str
    prediction_result: Dict[str, Any]
    confidence_score: float
    risk_level: Optional[str] = "LOW"
    recommendations: List[str] = Field(default_factory=list)
    latency_ms: float
