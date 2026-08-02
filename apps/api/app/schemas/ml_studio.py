import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ==========================================
# DATASET SCHEMAS
# ==========================================


class DatasetVersionCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    version: str = Field(..., example="v1.0")
    storage_path: str | None = None
    schema_json: dict[str, str] = Field(default_factory=dict)
    statistics_json: dict[str, Any] = Field(default_factory=dict)
    validation_json: dict[str, Any] = Field(default_factory=dict)


class DatasetVersionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)

    id: uuid.UUID
    dataset_id: uuid.UUID
    version: str
    storage_path: str | None
    schema_json: dict[str, Any]
    statistics_json: dict[str, Any]
    validation_json: dict[str, Any]
    status: str
    created_at: datetime


class DatasetCreate(BaseModel):
    code: str = Field(..., example="DS-HR-ATTRITION")
    name: str = Field(..., example="Employee Attrition Dataset")
    description: str | None = None
    domain: str = Field(default="HR", example="HR")
    format: str = Field(default="CSV", example="CSV")
    row_count: int = Field(default=1000)
    file_size_bytes: int = Field(default=250000)
    target_column: str | None = Field(default="left_company")
    features: list[str] = Field(default_factory=list)
    lineage_json: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class DatasetResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    code: str
    name: str
    description: str | None
    domain: str
    format: str
    status: str
    row_count: int
    file_size_bytes: int
    target_column: str | None
    features: list[str]
    lineage_json: dict[str, Any]
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    versions: list[DatasetVersionResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class DatasetPreviewResponse(BaseModel):
    columns: list[str]
    data_types: dict[str, str]
    rows: list[dict[str, Any]]
    total_rows: int


class DatasetValidationResponse(BaseModel):
    dataset_id: uuid.UUID
    version: str
    status: str  # PASSED, FAILED, WARNING
    checks_performed: int
    passed_checks: int
    failed_checks: int
    details: list[dict[str, Any]]


# ==========================================
# NOTEBOOK SCHEMAS
# ==========================================


class NotebookCell(BaseModel):
    id: str
    cell_type: str = Field(..., example="code")  # code, markdown
    code: str
    outputs: list[dict[str, Any]] = Field(default_factory=list)
    execution_count: int | None = None


class NotebookCreate(BaseModel):
    code: str = Field(..., example="NB-EDA-01")
    title: str = Field(..., example="Data Exploration & Feature Engineering")
    description: str | None = None
    language: str = Field(default="PYTHON")
    author: str = Field(default="Senior Data Scientist")
    runtime_env: str = Field(default="Python 3.11 ML CPU")
    cells_json: list[NotebookCell] = Field(default_factory=list)


class NotebookResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    code: str
    title: str
    description: str | None
    language: str
    author: str
    runtime_env: str
    status: str
    cells_json: list[dict[str, Any]]
    execution_logs: list[dict[str, Any]]
    version: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotebookExecutionResponse(BaseModel):
    notebook_id: uuid.UUID
    status: str  # SUCCESS, ERROR
    execution_time_seconds: float
    cell_results: list[dict[str, Any]]
    logs: list[str]


# ==========================================
# REGISTERED MODEL & APPROVAL SCHEMAS
# ==========================================


class RegisteredModelCreate(BaseModel):
    model_code: str = Field(..., example="MDL-ATTRITION-XGB")
    name: str = Field(..., example="XGBoost Attrition Predictor")
    description: str | None = None
    model_type: str = Field(default="CLASSIFICATION")
    ml_framework: str = Field(default="XGBOOST")
    business_domain: str = Field(default="HR")
    target_column: str | None = Field(default="left_company")
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class RegisteredModelResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    model_code: str
    name: str
    description: str | None
    model_type: str
    ml_framework: str
    business_domain: str
    target_column: str | None
    current_version: str
    stage: str
    approval_status: str
    approval_notes: str | None
    approved_by: str | None
    approved_at: datetime | None
    metadata_json: dict[str, Any]
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApprovalRequest(BaseModel):
    approval_status: str = Field(..., example="APPROVED")  # APPROVED, REJECTED
    approved_by: str = Field(..., example="Principal AI Architect")
    approval_notes: str | None = Field(
        default="Passed all threshold evaluation metrics and compliance checks."
    )


class PromotionRequest(BaseModel):
    stage: str = Field(
        ..., example="PRODUCTION"
    )  # DRAFT, CANDIDATE, APPROVED, STAGING, PRODUCTION, ARCHIVED


# ==========================================
# PACKAGING & CONTAINER SCHEMAS
# ==========================================


class ModelArtifactCreate(BaseModel):
    model_id: uuid.UUID
    version: str = Field(default="v1.0.0")
    artifact_type: str = Field(default="JOBLIB")
    file_path: str | None = None
    checksum: str | None = None
    file_size_bytes: int = Field(default=15400000)
    inference_config_json: dict[str, Any] = Field(default_factory=dict)
    runtime_requirements_json: dict[str, Any] = Field(default_factory=dict)
    container_metadata_json: dict[str, Any] = Field(default_factory=dict)


class ModelArtifactResponse(BaseModel):
    id: uuid.UUID
    model_id: uuid.UUID
    version: str
    artifact_type: str
    file_path: str | None
    checksum: str | None
    file_size_bytes: int
    inference_config_json: dict[str, Any]
    runtime_requirements_json: dict[str, Any]
    container_metadata_json: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class PackagingPreparationResponse(BaseModel):
    model_id: uuid.UUID
    version: str
    artifact_bundle_path: str
    dockerfile_template: str
    requirements_txt: str
    entrypoint_py: str
    checksum: str


# ==========================================
# EVALUATION REPORT SCHEMAS
# ==========================================


class EvaluationReportCreate(BaseModel):
    model_id: uuid.UUID
    model_version: str = Field(default="v1.0.0")
    evaluation_name: str = Field(..., example="Standard Test Evaluation")


class EvaluationReportResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    model_id: uuid.UUID
    model_version: str
    evaluation_name: str
    roc_curve_json: dict[str, Any]
    precision_recall_curve_json: dict[str, Any]
    confusion_matrix_json: dict[str, Any]
    regression_metrics_json: dict[str, Any]
    feature_importance_json: dict[str, Any]
    learning_curve_json: dict[str, Any]
    calibration_curve_json: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# EXPLAINABILITY SCHEMAS
# ==========================================


class LocalExplainRequest(BaseModel):
    model_id: uuid.UUID
    model_version: str = Field(default="v1.0.0")
    input_features: dict[str, Any]


class ExplainabilityReportResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    model_id: uuid.UUID
    model_version: str
    shap_data_json: dict[str, Any]
    lime_data_json: dict[str, Any]
    permutation_importance_json: dict[str, Any]
    global_explanation_json: dict[str, Any]
    local_explanation_json: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# MODEL COMPARISON SCHEMAS
# ==========================================


class ModelComparisonItem(BaseModel):
    model_id: uuid.UUID
    model_code: str
    name: str
    version: str
    framework: str
    accuracy: float
    f1_score: float
    precision: float
    recall: float
    rmse: float
    inference_latency_ms: float
    memory_mb: float
    training_time_sec: float
    top_features: list[dict[str, Any]]


class ModelComparisonResponse(BaseModel):
    compared_models: list[ModelComparisonItem]
    winner_by_accuracy: str
    winner_by_latency: str
