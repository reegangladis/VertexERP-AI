import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.data_engineering_service import DataEngineeringService
from app.schemas.data_engineering import (
    ETLJobCreate,
    ETLJobResponse,
    ETLRunResponse,
    PipelineLogResponse,
    DatasetCreate,
    DatasetResponse,
    DatasetVersionResponse,
    MetadataCatalogResponse,
    FeatureGroupCreate,
    FeatureGroupResponse,
    FeatureRegisterCreate,
    FeatureRegistryResponse,
    DataQualityReportResponse,
    LineageGraphResponse,
    DataLakeObjectResponse,
    MDMGoldenRecordResponse,
    DataEngineeringMonitoringSummary,
)

router = APIRouter()

# Default test org ID for API demonstration
DEFAULT_ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


# =========================================================================
# ETL / ELT PIPELINES & JOBS
# =========================================================================
@router.get("/etl-jobs", response_model=List[ETLJobResponse])
async def list_etl_jobs(db: AsyncSession = Depends(get_db)):
    """Fetch all enterprise ETL/ELT job definitions."""
    service = DataEngineeringService(db)
    return await service.get_etl_jobs(DEFAULT_ORG_ID)


@router.post("/etl-jobs", response_model=ETLJobResponse, status_code=status.HTTP_201_CREATED)
async def create_etl_job(payload: ETLJobCreate, db: AsyncSession = Depends(get_db)):
    """Create a new ETL pipeline job definition."""
    service = DataEngineeringService(db)
    return await service.create_etl_job(DEFAULT_ORG_ID, payload)


@router.post("/etl-jobs/{job_id}/run", response_model=ETLRunResponse)
async def trigger_pipeline_run(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Trigger execution run for an ETL pipeline job."""
    service = DataEngineeringService(db)
    try:
        return await service.trigger_pipeline_run(job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/runs/{run_id}/logs", response_model=List[PipelineLogResponse])
async def get_pipeline_run_logs(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Fetch execution logs for a pipeline run."""
    service = DataEngineeringService(db)
    return await service.get_run_logs(run_id)


# =========================================================================
# DATASETS & CATALOG
# =========================================================================
@router.get("/datasets", response_model=List[DatasetResponse])
async def list_datasets(db: AsyncSession = Depends(get_db)):
    """List all analytics datasets in the catalog."""
    service = DataEngineeringService(db)
    return await service.get_datasets(DEFAULT_ORG_ID)


@router.post("/datasets", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(payload: DatasetCreate, db: AsyncSession = Depends(get_db)):
    """Register a new analytics dataset."""
    service = DataEngineeringService(db)
    return await service.create_dataset(DEFAULT_ORG_ID, payload)


@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Fetch dataset details by ID."""
    service = DataEngineeringService(db)
    ds = await service.get_dataset_by_id(dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return ds


@router.post("/datasets/generate-root-files")
async def generate_root_datasets_files(db: AsyncSession = Depends(get_db)):
    """Export standard JSON analytics datasets to root datasets/ directory."""
    service = DataEngineeringService(db)
    service.generate_sample_datasets_on_disk()
    return {"message": "Successfully generated analytics datasets in root datasets/ directory."}


@router.get("/metadata", response_model=List[MetadataCatalogResponse])
async def search_metadata_catalog(dataset_id: Optional[uuid.UUID] = None, db: AsyncSession = Depends(get_db)):
    """Search metadata catalog and business dictionary."""
    service = DataEngineeringService(db)
    return await service.get_metadata_catalog(dataset_id)


# =========================================================================
# FEATURE STORE (AI-READY)
# =========================================================================
@router.get("/feature-groups", response_model=List[FeatureGroupResponse])
async def list_feature_groups(db: AsyncSession = Depends(get_db)):
    """List registered Feature Groups in the Feature Store."""
    service = DataEngineeringService(db)
    return await service.get_feature_groups(DEFAULT_ORG_ID)


@router.post("/feature-groups", response_model=FeatureGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_feature_group(payload: FeatureGroupCreate, db: AsyncSession = Depends(get_db)):
    """Register a new Feature Group."""
    service = DataEngineeringService(db)
    return await service.create_feature_group(DEFAULT_ORG_ID, payload)


@router.post("/features", response_model=FeatureRegistryResponse, status_code=status.HTTP_201_CREATED)
async def register_feature(payload: FeatureRegisterCreate, db: AsyncSession = Depends(get_db)):
    """Register an individual feature into a Feature Group."""
    service = DataEngineeringService(db)
    return await service.register_feature(payload)


# =========================================================================
# DATA QUALITY
# =========================================================================
@router.get("/data-quality", response_model=List[DataQualityReportResponse])
async def get_data_quality_reports(db: AsyncSession = Depends(get_db)):
    """List data quality profiling inspection reports."""
    service = DataEngineeringService(db)
    return await service.get_quality_reports(DEFAULT_ORG_ID)


@router.post("/data-quality/validate", response_model=DataQualityReportResponse)
async def validate_table_quality(table_name: str, db: AsyncSession = Depends(get_db)):
    """Run data quality validation rules against a target table or dataset."""
    service = DataEngineeringService(db)
    return await service.run_data_quality_inspection(DEFAULT_ORG_ID, table_name)


# =========================================================================
# DATA LINEAGE
# =========================================================================
@router.get("/lineage", response_model=LineageGraphResponse)
async def get_lineage_graph(db: AsyncSession = Depends(get_db)):
    """Fetch pipeline and dataset lineage DAG graph."""
    service = DataEngineeringService(db)
    return await service.get_lineage_graph(DEFAULT_ORG_ID)


# =========================================================================
# DATA LAKE & MASTER DATA MANAGEMENT (MDM)
# =========================================================================
@router.get("/datalake/objects", response_model=List[DataLakeObjectResponse])
async def list_data_lake_objects(zone: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """List objects in Data Lake zones (RAW, PROCESSED, CURATED, ARCHIVE)."""
    service = DataEngineeringService(db)
    return await service.get_data_lake_objects(DEFAULT_ORG_ID, zone)


@router.get("/master-data/records", response_model=List[MDMGoldenRecordResponse])
async def list_mdm_golden_records(entity_type: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """List Master Data Management (MDM) golden record entities."""
    service = DataEngineeringService(db)
    return await service.get_mdm_golden_records(DEFAULT_ORG_ID, entity_type)


# =========================================================================
# MONITORING DASHBOARD API
# =========================================================================
@router.get("/monitoring/summary", response_model=DataEngineeringMonitoringSummary)
async def get_monitoring_summary(db: AsyncSession = Depends(get_db)):
    """Fetch Data Engineering platform system status, metrics, and data freshness audit."""
    service = DataEngineeringService(db)
    return await service.get_monitoring_summary(DEFAULT_ORG_ID)
