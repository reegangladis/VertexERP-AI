import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ETL Jobs Schemas
class ETLJobCreate(BaseModel):
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    source_type: str = Field(..., max_length=50)
    target_type: str = Field(..., max_length=50)
    frequency: str = Field("HOURLY", max_length=50)
    schedule_cron: Optional[str] = None
    retry_limit: int = 3
    configuration: Optional[Dict[str, Any]] = None
    priority: int = 1
    is_incremental: bool = True


class ETLJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: Optional[str]
    source_type: str
    target_type: str
    frequency: str
    schedule_cron: Optional[str]
    status: str
    retry_limit: int
    configuration: Optional[Dict[str, Any]]
    priority: int
    is_incremental: bool
    created_at: datetime
    updated_at: datetime


class ETLRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    run_number: int
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    rows_extracted: int
    rows_transformed: int
    rows_loaded: int
    error_message: Optional[str]
    execution_params: Optional[Dict[str, Any]]


class PipelineLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    run_id: uuid.UUID
    timestamp: datetime
    log_level: str
    phase: str
    message: str
    details: Optional[Dict[str, Any]]


# Datasets & Catalog Schemas
class DatasetCreate(BaseModel):
    name: str = Field(..., max_length=150)
    slug: str = Field(..., max_length=150)
    category: str = Field(..., max_length=50)
    description: Optional[str] = None
    schema_definition: Dict[str, Any]
    update_frequency: str = "DAILY"
    ownership_team: str = "Data Engineering"
    data_steward: Optional[str] = None


class DatasetVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_id: uuid.UUID
    version_tag: str
    snapshot_path: str
    record_count: int
    checksum: Optional[str]
    schema_changes: Optional[Dict[str, Any]]
    created_at: datetime


class MetadataCatalogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_id: uuid.UUID
    column_name: str
    data_type: str
    business_definition: Optional[str]
    is_pii: bool
    classification: str
    data_steward: Optional[str]
    tags: Optional[List[str]]


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    slug: str
    category: str
    description: Optional[str]
    schema_definition: Dict[str, Any]
    update_frequency: str
    record_count: int
    size_bytes: int
    data_lake_path: Optional[str]
    ownership_team: str
    data_steward: Optional[str]
    created_at: datetime
    updated_at: datetime


# Feature Store Schemas
class FeatureGroupCreate(BaseModel):
    group_name: str = Field(..., max_length=150)
    entity_name: str = Field(..., max_length=100)
    entity_key: str = Field(..., max_length=100)
    description: Optional[str] = None
    online_enabled: bool = True
    offline_table: str = Field(..., max_length=150)
    owner: str = "ML Platform Team"
    tags: Optional[List[str]] = None


class FeatureRegisterCreate(BaseModel):
    feature_group_id: uuid.UUID
    feature_name: str = Field(..., max_length=150)
    data_type: str = Field(..., max_length=50)
    transformation_sql: Optional[str] = None
    description: Optional[str] = None
    version: str = "1.0"
    aggregation_window: Optional[str] = "30D"
    ml_feature_type: str = "NUMERICAL"
    online_ttl_seconds: int = 86400


class FeatureRegistryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    feature_group_id: uuid.UUID
    feature_name: str
    data_type: str
    transformation_sql: Optional[str]
    description: Optional[str]
    version: str
    status: str
    aggregation_window: Optional[str]
    ml_feature_type: str
    online_ttl_seconds: int
    created_at: datetime


class FeatureGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    group_name: str
    entity_name: str
    entity_key: str
    description: Optional[str]
    online_enabled: bool
    offline_table: str
    owner: str
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    features: List[FeatureRegistryResponse] = []


# Data Quality Schemas
class QualityValidationRule(BaseModel):
    rule_name: str
    rule_type: str  # NULL_CHECK, DUPLICATE_CHECK, SCHEMA_CHECK, REFERENTIAL_CHECK
    status: str  # PASSED, FAILED
    affected_rows: int = 0
    message: str


class DataQualityReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    table_name: str
    dataset_id: Optional[uuid.UUID]
    run_id: Optional[uuid.UUID]
    passed_count: int
    failed_count: int
    quality_score: float
    rule_results: List[Dict[str, Any]]
    null_violations: int
    duplicate_violations: int
    schema_violations: int
    referential_violations: int
    created_at: datetime


# Lineage Graph Schemas
class LineageNode(BaseModel):
    id: str
    label: str
    type: str  # SOURCE_TABLE, RAW_ZONE, PROCESSED_ZONE, DIMENSION, FACT, FEATURE, DATASET
    category: str


class LineageEdge(BaseModel):
    source: str
    target: str
    label: str
    type: str


class LineageGraphResponse(BaseModel):
    nodes: List[LineageNode]
    edges: List[LineageEdge]


# Data Lake Schemas
class DataLakeObjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    zone: str
    object_path: str
    file_format: str
    file_size_bytes: int
    record_count: int
    source_domain: str
    checksum: Optional[str]
    created_at: datetime


# Master Data Management (MDM) Schemas
class MDMGoldenRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    entity_type: str
    golden_id: str
    master_data: Dict[str, Any]
    confidence_score: float
    match_rules_applied: List[str]
    source_system_ids: List[str]
    status: str
    created_at: datetime
    updated_at: datetime


# Monitoring Summary Schema
class DataEngineeringMonitoringSummary(BaseModel):
    total_pipelines: int
    active_pipelines: int
    failed_pipelines_24h: int
    total_rows_processed_24h: int
    overall_quality_score: float
    data_lake_total_size_gb: float
    feature_groups_count: int
    registered_features_count: int
    data_freshness_status: str
