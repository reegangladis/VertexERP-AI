from app.services.ml.business_modules import BusinessMLModulesService
from app.services.ml.evaluation_service import EvaluationService
from app.services.ml.feature_engineering import (
    CategoricalEncoder,
    DataScaler,
    FeaturePipeline,
    MissingValueHandler,
    OutlierHandler,
)
from app.services.ml.models import MLModelAdapter


def test_categorical_one_hot_encoding():
    data = [{"city": "New York"}, {"city": "London"}, {"city": "New York"}]
    encoded = CategoricalEncoder.one_hot_encode(data, "city")
    assert len(encoded) == 3
    assert encoded[0]["city_New York"] == 1.0
    assert encoded[0]["city_London"] == 0.0


def test_scaler_transformations():
    vals = [10.0, 20.0, 30.0, 40.0, 50.0]
    min_max = DataScaler.min_max_scaler(vals)
    assert min_max[0] == 0.0
    assert min_max[-1] == 1.0

    standard = DataScaler.standard_scaler(vals)
    assert len(standard) == 5


def test_outlier_and_missing_value_handlers():
    raw_vals = [10.0, 12.0, 14.0, 15.0, 100.0]
    clipped = OutlierHandler.handle_iqr(raw_vals)
    assert clipped[-1] < 100.0

    missing_vals = [10.0, None, 30.0]
    imputed = MissingValueHandler.impute_numerical(missing_vals, strategy="mean")
    assert imputed[1] == 20.0


def test_feature_pipeline_fit_transform():
    pipeline = FeaturePipeline(
        [
            {"action": "impute", "column": "age", "strategy": "mean"},
            {"action": "scale", "column": "age"},
        ]
    )
    data = [{"age": 20}, {"age": None}, {"age": 40}]
    processed = pipeline.fit_transform(data)
    assert processed[1]["age"] == 30.0
    assert "age_scaled" in processed[0]


def test_ml_model_adapter_fit_predict():
    adapter = MLModelAdapter(model_type="CLASSIFICATION", ml_framework="XGBOOST")
    X = [[0.1, 0.2, 0.3], [0.8, 0.9, 0.7]]
    y = [0, 1]

    fit_res = adapter.fit(X, y)
    assert fit_res["status"] == "SUCCESS"
    assert fit_res["framework"] == "XGBOOST"

    preds = adapter.predict(X)
    assert len(preds) == 2
    assert "probability" in preds[0]


def test_evaluation_metrics_computation():
    y_true = [1, 0, 1, 1, 0, 0, 1, 0]
    y_pred = [1, 0, 1, 0, 0, 0, 1, 1]

    class_metrics = EvaluationService.compute_classification_metrics(y_true, y_pred)
    assert "accuracy" in class_metrics
    assert "confusion_matrix" in class_metrics

    reg_true = [100.0, 200.0, 300.0]
    reg_pred = [110.0, 190.0, 310.0]
    reg_metrics = EvaluationService.compute_regression_metrics(reg_true, reg_pred)
    assert reg_metrics["mae"] == 10.0


def test_business_ml_modules():
    attr_res = BusinessMLModulesService.predict_attrition(
        {"satisfaction_score": 1.5, "overtime_hours": 25}
    )
    assert attr_res.module_key == "attrition"
    assert attr_res.risk_level == "HIGH"

    fraud_res = BusinessMLModulesService.predict_fraud(
        {"transaction_amount": 15000, "is_foreign_ip": True, "hour_of_day": 2}
    )
    assert fraud_res.module_key == "fraud"
    assert fraud_res.prediction_result["is_fraudulent"] is True
