import pytest

from app.services.ml.business_modules import BusinessMLModulesService
from app.services.ml.dataset_service import MLDatasetGenerator
from app.services.ml.training_service import TrainingService


@pytest.mark.asyncio
async def test_dataset_generator_functions():
    hr_data = MLDatasetGenerator.generate_hr_attrition_dataset(records=10)
    assert len(hr_data) == 10
    assert "attrition_flag" in hr_data[0]

    crm_data = MLDatasetGenerator.generate_crm_churn_dataset(records=10)
    assert len(crm_data) == 10
    assert "churn_flag" in crm_data[0]

    sales_data = MLDatasetGenerator.generate_sales_forecasting_dataset(records=10)
    assert len(sales_data) == 10
    assert "target_quarterly_sales" in sales_data[0]


@pytest.mark.asyncio
async def test_business_ml_modules_predictions():
    # HR Attrition
    attr_res = BusinessMLModulesService.predict_attrition(
        {"tenure_months": 12, "satisfaction_score": 2.1, "overtime_hours": 25}
    )
    assert attr_res.module_key == "attrition"
    assert "attrition_probability" in attr_res.prediction_result

    # Sales Forecast
    sales_res = BusinessMLModulesService.predict_sales_forecast(
        {"historical_sales": 150000, "growth_rate": 0.12, "deals_in_pipeline": 15}
    )
    assert sales_res.module_key == "sales_forecasting"
    assert "projected_quarterly_sales" in sales_res.prediction_result

    # Customer Churn
    churn_res = BusinessMLModulesService.predict_customer_churn(
        {"support_tickets_opened": 10, "nps_score": 3, "days_since_last_login": 35}
    )
    assert churn_res.module_key == "churn"
    assert (
        "churn_probability" in churn_res.prediction_result
        or "churn_risk" in churn_res.prediction_result
    )

    # Inventory Optimization
    inv_res = BusinessMLModulesService.predict_inventory_optimization(
        {"current_stock": 100, "reorder_point": 250, "holding_cost": 4.5}
    )
    assert inv_res.module_key == "inventory_opt"
    assert "reorder_flag" in inv_res.prediction_result

    # Fraud Detection
    fraud_res = BusinessMLModulesService.predict_fraud(
        {"transaction_amount": 25000, "is_foreign_ip": True, "hour_of_day": 3}
    )
    assert fraud_res.module_key == "fraud"
    assert "fraud_probability_score" in fraud_res.prediction_result


@pytest.mark.asyncio
async def test_training_service_split_and_folds():
    data = list(range(100))
    train, test = TrainingService.train_test_split(data, test_size=0.2, seed=42)
    assert len(train) == 80
    assert len(test) == 20

    folds = TrainingService.k_fold_cross_validation(data, k=5)
    assert len(folds) == 5
    assert len(folds[0][1]) == 20
    assert len(folds[0][0]) == 80
