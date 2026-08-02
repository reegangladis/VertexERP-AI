import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.data_engineering_service import DataEngineeringService


@pytest.mark.asyncio
async def test_integration_monitoring_summary():
    db_mock = AsyncMock()
    service = DataEngineeringService(db_mock)
    org_id = uuid.uuid4()

    mock_job = MagicMock(status="ACTIVE")
    mock_fg = MagicMock(features=[MagicMock(), MagicMock()])

    service.repo.get_jobs_by_org = AsyncMock(return_value=[mock_job])
    service.repo.get_feature_groups_by_org = AsyncMock(return_value=[mock_fg])

    summary = await service.get_monitoring_summary(org_id)
    assert summary.active_pipelines == 1
    assert summary.feature_groups_count == 1
    assert summary.registered_features_count == 2
    assert summary.overall_quality_score == 99.8


@pytest.mark.asyncio
async def test_integration_data_lake_and_mdm():
    db_mock = AsyncMock()
    service = DataEngineeringService(db_mock)
    org_id = uuid.uuid4()

    service.repo.get_data_lake_objects = AsyncMock(return_value=[])
    service.repo.create_data_lake_object = AsyncMock(side_effect=lambda o: o)
    service.repo.get_mdm_golden_records = AsyncMock(return_value=[])
    service.repo.create_mdm_record = AsyncMock(side_effect=lambda r: r)

    lake_objs = await service.get_data_lake_objects(org_id)
    assert len(lake_objs) == 4

    mdm_recs = await service.get_mdm_golden_records(org_id)
    assert len(mdm_recs) == 4
