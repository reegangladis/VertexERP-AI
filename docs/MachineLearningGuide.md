# Enterprise Machine Learning Platform Guide

## Architecture Overview
The **Enterprise Machine Learning Platform** (Phase 11) provides reusable, production-ready ML infrastructure across VertexERP AI. Following Clean Architecture, DDD, and SOLID principles, it unifies Feature Engineering, Model Training, Model Evaluation, Experiment Tracking, Model Registry, and Inference without requiring deployment pipelines yet.

---

## Supported Frameworks
1. **scikit-learn**: Classic Supervised ML (LogisticRegression, RandomForest, DecisionTrees).
2. **XGBoost**: Extreme Gradient Boosting for tabular Classification & Regression.
3. **LightGBM**: Fast, distributed gradient boosting framework.
4. **CatBoost**: Categorical feature-native gradient boosting.
5. **TensorFlow**: Deep Neural Networks and multi-layer perceptrons.
6. **PyTorch**: Dynamic graph deep learning models.
7. **Prophet**: Additive time-series forecasting engine.

---

## Supported Task Types
- **Classification**: Binary & Multi-Class predictions.
- **Regression**: Continuous numerical target estimations.
- **Clustering**: Unsupervised grouping (K-Means, DBSCAN).
- **Time Series Forecasting**: Seasonal & trend forecasting.
- **Recommendation Engine**: Matrix factorization & item filtering.
- **Anomaly Detection**: Outlier identification (IsolationForest).

---

## Feature Engineering Engine
The `FeaturePipeline` orchestrates reusable transformers:
- **Categorical Encoders**: `one_hot_encode`, `ordinal_encode`.
- **Feature Scalers**: `standard_scaler`, `min_max_scaler`, `robust_scaler`.
- **Outlier Handling**: `handle_iqr` truncation, `handle_zscore` clipping.
- **Missing Value Imputation**: `impute_numerical` (mean, median, mode, constant).
- **Feature Selection**: Variance threshold filtering.

---

## Pre-built Business Domain Modules
- **Employee Attrition Risk**: HR Turnover probability & flight risk factors.
- **Sales Pipeline Forecasting**: CRM quarterly revenue forecasting.
- **Demand Forecasting**: Inventory procurement target calculation.
- **Inventory Optimization**: EOQ & stockout risk score.
- **Customer Churn Predictor**: Customer retention risk scoring.
- **Fraud Detection**: Financial transaction risk scoring.
- **Quality Defect Predictor**: Manufacturing tolerance pass/fail.
- **Predictive Maintenance**: Machine remaining useful life (RUL) in days.
- **Revenue Forecasting**: Net Retention Rate (NRR) and ARR projection.
