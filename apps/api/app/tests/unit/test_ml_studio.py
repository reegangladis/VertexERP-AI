import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from app.services.ml_studio_service import MLStudioService
from app.models.ml_studio import DatasetRegistry, RegisteredModel
from app.schemas.ml_studio import (
    DatasetCreate,
    NotebookCreate,
    RegisteredModelCreate,
    ApprovalRequest,
    PromotionRequest,
    LocalExplainRequest,
)


@pytest.mark.asyncio
async def test_dataset_statistics_calculation():
    """Test calculation of summary statistics for dataset features."""
    service = MLStudioService(db=AsyncMock())
    dataset = DatasetRegistry(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        code="DS-UNIT-01",
        name="Unit Dataset",
        row_count=1000,
        features=["overtime_hours", "monthly_income"],
        target_column="left_company"
    )
    stats = service.calculate_dataset_statistics(dataset)
    assert stats["total_rows"] == 1000
    assert "overtime_hours" in stats["column_statistics"]
    assert stats["column_statistics"]["overtime_hours"]["data_type"] == "float64"


@pytest.mark.asyncio
async def test_notebook_template_generation():
    """Test notebook template listing."""
    service = MLStudioService(db=AsyncMock())
    templates = service.get_notebook_templates()
    assert len(templates) == 3
    assert templates[0]["id"] == "tpl_eda"


@pytest.mark.asyncio
async def test_local_prediction_explanation():
    """Test local instance prediction waterfall explanation."""
    service = MLStudioService(db=AsyncMock())
    request = LocalExplainRequest(
        model_id=uuid.uuid4(),
        model_version="v1.0.0",
        input_features={"OverTime": "Yes", "MonthlyIncome": 3200, "DistanceFromHome": 22}
    )
    res = await service.explain_local_prediction(request)
    assert res["prediction_label"] == "HIGH_RISK"
    assert len(res["waterfall_contributions"]) == 4


@pytest.mark.asyncio
async def test_model_packaging_preparation():
    """Test Dockerfile and entrypoint py generation for model packaging."""
    service = MLStudioService(db=AsyncMock())
    service.model_repo.get_by_id = AsyncMock(return_value=None)
    res = await service.prepare_packaging(uuid.uuid4())
    assert "FROM python:3.11-slim" in res["dockerfile_template"]
    assert "import joblib" in res["entrypoint_py"]
    assert "checksum" in res
