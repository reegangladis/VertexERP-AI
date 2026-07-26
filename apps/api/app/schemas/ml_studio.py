from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import uuid


# ==========================================
# DATASET SCHEMAS
# ==========================================

class DatasetVersionCreate(BaseModel):
    version: str = Field(..., example="v1.0")
    storage_path: Optional[str] = None
    schema_json: Dict[str, str] = Field(default_factory=dict)
    statistics_json: Dict[str, Any] = Field(default_factory=dict)
    validation_json: Dict[str, Any] = Field(default_factory=dict)


class DatasetVersionResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    version: str
    storage_path: Optional[str]
    schema_json: Dict[str, Any]
    statistics_json: Dict[str, Any]
    validation_json: Dict[str, Any]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DatasetCreate(BaseModel):
    code: str = Field(..., example="DS-HR-ATTRITION")
    name: str = Field(..., example="Employee Attrition Dataset")
    description: Optional[str] = None
    domain: str = Field(default="HR", example="HR")
    format: str = Field(default="CSV", example="CSV")
    row_count: int = Field(default=1000)
    file_size_bytes: int = Field(default=250000)
    target_column: Optional[str] = Field(default="left_company")
    features: List[str] = Field(default_factory=list)
    lineage_json: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class DatasetResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    code: str
    name: str
    description: Optional[str]
    domain: str
    format: str
    status: str
    row_count: int
    file_size_bytes: int
    target_column: Optional[str]
    features: List[str]
    lineage_json: Dict[str, Any]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    versions: List[DatasetVersionResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class DatasetPreviewResponse(BaseModel):
    columns: List[str]
    data_types: Dict[str, str]
    rows: List[Dict[str, Any]]
    total_rows: int


class DatasetValidationResponse(BaseModel):
    dataset_id: uuid.UUID
    version: str
    status: str  # PASSED, FAILED, WARNING
    checks_performed: int
    passed_checks: int
    failed_checks: int
    details: List[Dict[str, Any]]


# ==========================================
# NOTEBOOK SCHEMAS
# ==========================================

class NotebookCell(BaseModel):
    id: str
    cell_type: str = Field(..., example="code")  # code, markdown
    code: str
    outputs: List[Dict[str, Any]] = Field(default_factory=list)
    execution_count: Optional[int] = None


class NotebookCreate(BaseModel):
    code: str = Field(..., example="NB-EDA-01")
    title: str = Field(..., example="Data Exploration & Feature Engineering")
    description: Optional[str] = None
    language: str = Field(default="PYTHON")
    author: str = Field(default="Senior Data Scientist")
    runtime_env: str = Field(default="Python 3.11 ML CPU")
    cells_json: List[NotebookCell] = Field(default_factory=list)


class NotebookResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    code: str
    title: str
    description: Optional[str]
    language: str
    author: str
    runtime_env: str
    status: str
    cells_json: List[Dict[str, Any]]
    execution_logs: List[Dict[str, Any]]
    version: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotebookExecutionResponse(BaseModel):
    notebook_id: uuid.UUID
    status: str  # SUCCESS, ERROR
    execution_time_seconds: float
    cell_results: List[Dict[str, Any]]
    logs: List[str]


# ==========================================
# REGISTERED MODEL & APPROVAL SCHEMAS
# ==========================================

class RegisteredModelCreate(BaseModel):
    model_code: str = Field(..., example="MDL-ATTRITION-XGB")
    name: str = Field(..., example="XGBoost Attrition Predictor")
    description: Optional[str] = None
    model_type: str = Field(default="CLASSIFICATION")
    ml_framework: str = Field(default="XGBOOST")
    business_domain: str = Field(default="HR")
    target_column: Optional[str] = Field(default="left_company")
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class RegisteredModelResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    model_code: str
    name: str
    description: Optional[str]
    model_type: str
    ml_framework: str
    business_domain: str
    target_column: Optional[str]
    current_version: str
    stage: str
    approval_status: str
    approval_notes: Optional[str]
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    metadata_json: Dict[str, Any]
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApprovalRequest(BaseModel):
    approval_status: str = Field(..., example="APPROVED")  # APPROVED, REJECTED
    approved_by: str = Field(..., example="Principal AI Architect")
    approval_notes: Optional[str] = Field(default="Passed all threshold evaluation metrics and compliance checks.")


class PromotionRequest(BaseModel):
    stage: str = Field(..., example="PRODUCTION")  # DRAFT, CANDIDATE, APPROVED, STAGING, PRODUCTION, ARCHIVED


# ==========================================
# PACKAGING & CONTAINER SCHEMAS
# ==========================================

class ModelArtifactCreate(BaseModel):
    model_id: uuid.UUID
    version: str = Field(default="v1.0.0")
    artifact_type: str = Field(default="JOBLIB")
    file_path: Optional[str] = None
    checksum: Optional[str] = None
    file_size_bytes: int = Field(default=15400000)
    inference_config_json: Dict[str, Any] = Field(default_factory=dict)
    runtime_requirements_json: Dict[str, Any] = Field(default_factory=dict)
    container_metadata_json: Dict[str, Any] = Field(default_factory=dict)


class ModelArtifactResponse(BaseModel):
    id: uuid.UUID
    model_id: uuid.UUID
    version: str
    artifact_type: str
    file_path: Optional[str]
    checksum: Optional[str]
    file_size_bytes: int
    inference_config_json: Dict[str, Any]
    runtime_requirements_json: Dict[str, Any]
    container_metadata_json: Dict[str, Any]
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
    roc_curve_json: Dict[str, Any]
    precision_recall_curve_json: Dict[str, Any]
    confusion_matrix_json: Dict[str, Any]
    regression_metrics_json: Dict[str, Any]
    feature_importance_json: Dict[str, Any]
    learning_curve_json: Dict[str, Any]
    calibration_curve_json: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# EXPLAINABILITY SCHEMAS
# ==========================================

class LocalExplainRequest(BaseModel):
    model_id: uuid.UUID
    model_version: str = Field(default="v1.0.0")
    input_features: Dict[str, Any]


class ExplainabilityReportResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    model_id: uuid.UUID
    model_version: str
    shap_data_json: Dict[str, Any]
    lime_data_json: Dict[str, Any]
    permutation_importance_json: Dict[str, Any]
    global_explanation_json: Dict[str, Any]
    local_explanation_json: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


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
    top_features: List[Dict[str, Any]]


class ModelComparisonResponse(BaseModel):
    compared_models: List[ModelComparisonItem]
    winner_by_accuracy: str
    winner_by_latency: str
