import uuid
from unittest.mock import MagicMock
import pytest

from app.models.data_analytics_mlops_v15 import (
    Dataset,
    DriftReport,
    ETLJob,
    FeatureStore,
    MLModel,
    ModelVersion,
    PipelineJob,
)
from app.services.data_analytics_mlops import (
    DataPlatformAnalyticsService,
    DatasetETLService,
    DriftMonitoringEngine,
    FeatureStoreEngine,
    MLOpsEngine,
    PredictionEngine,
)


def create_mock_execute_result(return_value=None, list_value=None):
    result = MagicMock()
    result.scalar_one_or_none.return_value = return_value
    result.scalars.return_value.all.return_value = list_value if list_value is not None else []
    return result


@pytest.mark.asyncio
async def test_dataset_and_etl_pipeline_creation(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    service = DatasetETLService(mock_db_session)
    org_id = uuid.uuid4()

    from app.schemas.data_analytics_mlops import DatasetCreate, ETLJobCreate, PipelineJobCreate

    ds_payload = DatasetCreate(
        organization_id=org_id,
        dataset_name="Sales_Transactions_2026",
        dataset_type="Tabular",
        source="Snowflake Data Warehouse",
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),  # dup check
    ]
    ds = await service.create_dataset(ds_payload)
    assert ds is not None

    pipe_payload = PipelineJobCreate(
        organization_id=org_id,
        pipeline_name="Nightly_Sales_ETL_Airflow_DAG",
        schedule_cron="0 2 * * *",
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),
    ]
    pipe = await service.create_pipeline_job(pipe_payload)
    assert pipe is not None


@pytest.mark.asyncio
async def test_feature_store_creation(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    engine = FeatureStoreEngine(mock_db_session)

    from app.schemas.data_analytics_mlops import FeatureStoreCreate

    payload = FeatureStoreCreate(
        feature_name="customer_30d_avg_spend",
        feature_group="Customer_Features",
        data_type="FLOAT",
        description="Average purchase amount over past 30 days",
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),  # dup check
    ]
    feature = await engine.create_feature(payload)
    assert feature is not None


@pytest.mark.asyncio
async def test_mlops_model_registry_and_training(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    engine = MLOpsEngine(mock_db_session)
    org_id = uuid.uuid4()
    model_id = uuid.uuid4()
    dataset_id = uuid.uuid4()

    from app.schemas.data_analytics_mlops import MLModelCreate, ModelVersionCreate, TrainingJobCreate

    model_payload = MLModelCreate(
        organization_id=org_id,
        model_name="Customer_Churn_Predictor_XGBoost",
        algorithm="XGBoost",
        framework="scikit-learn",
        problem_type="Classification",
    )

    model_obj = MLModel(
        id=model_id,
        organization_id=org_id,
        model_name=model_payload.model_name,
        algorithm=model_payload.algorithm,
        current_version="v1.0.0",
        status="Production",
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),  # dup check
    ]
    model = await engine.register_model(model_payload)
    assert model is not None

    ver_payload = ModelVersionCreate(
        model_id=model_id,
        version="v1.1.0",
        metrics='{"accuracy": 0.945, "f1_score": 0.932}',
        artifact_path="s3://ml-artifacts/churn_model_v1.1.0.pkl",
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(model_obj),  # get model
        create_mock_execute_result(None),  # create version
        create_mock_execute_result(None),  # update model current_version
    ]
    ver = await engine.register_version(ver_payload)
    assert ver is not None

    train_payload = TrainingJobCreate(model_id=model_id, dataset_id=dataset_id)
    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),
    ]
    tjob = await engine.create_training_job(train_payload)
    assert tjob is not None


@pytest.mark.asyncio
async def test_online_prediction_service(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    engine = PredictionEngine(mock_db_session)
    ver_id = uuid.uuid4()

    ver_obj = ModelVersion(
        id=ver_id,
        model_id=uuid.uuid4(),
        version="v1.0.0",
        metrics='{"accuracy": 0.96}',
        artifact_path="s3://ml-artifacts/model.pkl",
    )

    from app.schemas.data_analytics_mlops import PredictionRequest

    pred_req = PredictionRequest(
        model_version_id=ver_id,
        input_data={"customer_id": "CUST-1002", "spend_30d": 1255.50},
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(ver_obj),  # get version
    ]
    result = await engine.run_online_prediction(pred_req)
    assert result is not None
    assert result.status == "Success"
    assert result.confidence_score > 0.90


@pytest.mark.asyncio
async def test_drift_monitoring_engine(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    engine = DriftMonitoringEngine(mock_db_session)
    model_id = uuid.uuid4()

    model_obj = MLModel(
        id=model_id,
        organization_id=uuid.uuid4(),
        model_name="Demand_Forecaster",
        algorithm="LightGBM",
    )

    from app.schemas.data_analytics_mlops import DriftReportCreate

    drift_req = DriftReportCreate(model_id=model_id, drift_type="Data Drift")

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(model_obj),  # get model
    ]
    report = await engine.generate_drift_report(drift_req)
    assert report is not None
    assert report.status == "Normal"


@pytest.mark.asyncio
async def test_data_platform_analytics_dashboard_summary(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None, [])
    service = DataPlatformAnalyticsService(mock_db_session)
    org_id = uuid.uuid4()

    summary = await service.get_dashboard_summary(org_id)
    assert summary.total_datasets >= 0
    assert summary.total_features_in_store >= 0
    assert summary.active_ml_models >= 0
