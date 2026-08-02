import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ETL Jobs Schemas
class ETLJobCreate(BaseModel):
    name: str = Field(..., max_length=150)
    description: str | None = None
    source_type: str = Field(..., max_length=50)
    target_type: str = Field(..., max_length=50)
    frequency: str = Field("HOURLY", max_length=50)
    schedule_cron: str | None = None
    retry_limit: int = 3
    configuration: dict[str, Any] | None = None
    priority: int = 1
    is_incremental: bool = True


class ETLJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None
    source_type: str
    target_type: str
    frequency: str
    schedule_cron: str | None
    status: str
    retry_limit: int
    configuration: dict[str, Any] | None
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
    end_time: datetime | None
    duration_seconds: float | None
    rows_extracted: int
    rows_transformed: int
    rows_loaded: int
    error_message: str | None
    execution_params: dict[str, Any] | None


class PipelineLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    run_id: uuid.UUID
    timestamp: datetime
    log_level: str
    phase: str
    message: str
    details: dict[str, Any] | None


# Datasets & Catalog Schemas
class DatasetCreate(BaseModel):
    name: str = Field(..., max_length=150)
    slug: str = Field(..., max_length=150)
    category: str = Field(..., max_length=50)
    description: str | None = None
    schema_definition: dict[str, Any]
    update_frequency: str = "DAILY"
    ownership_team: str = "Data Engineering"
    data_steward: str | None = None


class DatasetVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_id: uuid.UUID
    version_tag: str
    snapshot_path: str
    record_count: int
    checksum: str | None
    schema_changes: dict[str, Any] | None
    created_at: datetime


class MetadataCatalogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_id: uuid.UUID
    column_name: str
    data_type: str
    business_definition: str | None
    is_pii: bool
    classification: str
    data_steward: str | None
    tags: list[str] | None


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    slug: str
    category: str
    description: str | None
    schema_definition: dict[str, Any]
    update_frequency: str
    record_count: int
    size_bytes: int
    data_lake_path: str | None
    ownership_team: str
    data_steward: str | None
    created_at: datetime
    updated_at: datetime


# Feature Store Schemas
class FeatureGroupCreate(BaseModel):
    group_name: str = Field(..., max_length=150)
    entity_name: str = Field(..., max_length=100)
    entity_key: str = Field(..., max_length=100)
    description: str | None = None
    online_enabled: bool = True
    offline_table: str = Field(..., max_length=150)
    owner: str = "ML Platform Team"
    tags: list[str] | None = None


class FeatureRegisterCreate(BaseModel):
    feature_group_id: uuid.UUID
    feature_name: str = Field(..., max_length=150)
    data_type: str = Field(..., max_length=50)
    transformation_sql: str | None = None
    description: str | None = None
    version: str = "1.0"
    aggregation_window: str | None = "30D"
    ml_feature_type: str = "NUMERICAL"
    online_ttl_seconds: int = 86400


class FeatureRegistryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    feature_group_id: uuid.UUID
    feature_name: str
    data_type: str
    transformation_sql: str | None
    description: str | None
    version: str
    status: str
    aggregation_window: str | None
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
    description: str | None
    online_enabled: bool
    offline_table: str
    owner: str
    tags: list[str] | None
    created_at: datetime
    updated_at: datetime
    features: list[FeatureRegistryResponse] = []


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
    dataset_id: uuid.UUID | None
    run_id: uuid.UUID | None
    passed_count: int
    failed_count: int
    quality_score: float
    rule_results: list[dict[str, Any]]
    null_violations: int
    duplicate_violations: int
    schema_violations: int
    referential_violations: int
    created_at: datetime


# Lineage Graph Schemas
class LineageNode(BaseModel):
    id: str
    label: str
    type: (
        str  # SOURCE_TABLE, RAW_ZONE, PROCESSED_ZONE, DIMENSION, FACT, FEATURE, DATASET
    )
    category: str


class LineageEdge(BaseModel):
    source: str
    target: str
    label: str
    type: str


class LineageGraphResponse(BaseModel):
    nodes: list[LineageNode]
    edges: list[LineageEdge]


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
    checksum: str | None
    created_at: datetime


# Master Data Management (MDM) Schemas
class MDMGoldenRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    entity_type: str
    golden_id: str
    master_data: dict[str, Any]
    confidence_score: float
    match_rules_applied: list[str]
    source_system_ids: list[str]
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
