import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.data_engineering_service import DataEngineeringService
from app.schemas.data_engineering import ETLJobCreate, FeatureGroupCreate, FeatureRegisterCreate, DatasetCreate


@pytest.mark.asyncio
async def test_etl_job_creation_and_pipeline_trigger():
    db_mock = AsyncMock()
    service = DataEngineeringService(db_mock)
    org_id = uuid.uuid4()
    job_id = uuid.uuid4()

    mock_job = MagicMock()
    mock_job.id = job_id
    mock_job.is_incremental = True
    mock_job.source_type = "CRM"
    mock_job.target_type = "WAREHOUSE"

    service.repo.get_job_by_id = AsyncMock(return_value=mock_job)
    service.repo.get_runs_by_job = AsyncMock(return_value=[])
    service.repo.create_run = AsyncMock(side_effect=lambda r: r)
    service.repo.add_pipeline_log = AsyncMock()
    service.repo.update_run = AsyncMock(side_effect=lambda r_id, vals: MagicMock(id=r_id, **vals))

    run = await service.trigger_pipeline_run(job_id)
    assert run.status == "SUCCESS"
    assert run.rows_extracted == 1250
    assert run.rows_transformed == 1225


@pytest.mark.asyncio
async def test_data_quality_inspection_scoring():
    db_mock = AsyncMock()
    service = DataEngineeringService(db_mock)
    org_id = uuid.uuid4()

    service.repo.create_quality_report = AsyncMock(side_effect=lambda r: r)

    report = await service.run_data_quality_inspection(org_id, "fact_sales")
    assert report.quality_score == 100.0
    assert report.passed_count == 4
    assert report.null_violations == 0


@pytest.mark.asyncio
async def test_feature_store_registration():
    db_mock = AsyncMock()
    service = DataEngineeringService(db_mock)
    org_id = uuid.uuid4()
    group_id = uuid.uuid4()

    mock_group = MagicMock()
    mock_group.id = group_id
    mock_group.group_name = "customer_churn_features"

    service.repo.create_feature_group = AsyncMock(return_value=mock_group)

    fg_data = FeatureGroupCreate(
        group_name="customer_churn_features",
        entity_name="Customer",
        entity_key="customer_id",
        offline_table="curated_customer_features",
    )

    created_group = await service.create_feature_group(org_id, fg_data)
    assert created_group.group_name == "customer_churn_features"


@pytest.mark.asyncio
async def test_lineage_graph_dag_generation():
    db_mock = AsyncMock()
    service = DataEngineeringService(db_mock)
    org_id = uuid.uuid4()

    lineage = await service.get_lineage_graph(org_id)
    assert len(lineage.nodes) >= 5
    assert len(lineage.edges) >= 4
