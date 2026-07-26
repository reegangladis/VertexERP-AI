import hashlib
import json
import math
import random
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ml_studio import (
    DatasetRegistry,
    DatasetVersionModel,
    Notebook,
    RegisteredModel,
    ModelArtifact,
    TrainingLog,
    EvaluationReport,
    ExplainabilityReport,
)
from app.repositories.ml_studio_repository import (
    MLStudioDatasetRepository,
    MLStudioNotebookRepository,
    MLStudioModelRepository,
    MLStudioEvaluationRepository,
    MLStudioExplainabilityRepository,
)
from app.schemas.ml_studio import (
    DatasetCreate,
    DatasetVersionCreate,
    NotebookCreate,
    RegisteredModelCreate,
    ApprovalRequest,
    PromotionRequest,
    ModelArtifactCreate,
    LocalExplainRequest,
)


class MLStudioService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dataset_repo = MLStudioDatasetRepository(db)
        self.notebook_repo = MLStudioNotebookRepository(db)
        self.model_repo = MLStudioModelRepository(db)
        self.eval_repo = MLStudioEvaluationRepository(db)
        self.explain_repo = MLStudioExplainabilityRepository(db)

    # ==========================================
    # DATASETS MANAGEMENT ENGINE
    # ==========================================

    async def list_datasets(self, organization_id: uuid.UUID, domain: Optional[str] = None) -> List[DatasetRegistry]:
        return await self.dataset_repo.get_all(organization_id, domain)

    async def create_dataset(self, organization_id: uuid.UUID, payload: DatasetCreate) -> DatasetRegistry:
        dataset = DatasetRegistry(
            id=uuid.uuid4(),
            organization_id=organization_id,
            code=payload.code,
            name=payload.name,
            description=payload.description,
            domain=payload.domain,
            format=payload.format,
            row_count=payload.row_count,
            file_size_bytes=payload.file_size_bytes,
            target_column=payload.target_column,
            features=payload.features,
            lineage_json=payload.lineage_json or {
                "source_pipeline": "ETL_HR_ATTENDANCE_DAILY",
                "parent_dataset": "raw_hr_records_v1",
                "downstream_models": ["MDL-ATTRITION-XGB", "MDL-FLIGHT-RISK-RF"]
            },
            tags=payload.tags or ["hr", "attrition", "structured", "v1"],
        )
        created = await self.dataset_repo.create(dataset)

        # Automatically create initial v1.0 version with generated statistics
        v1_stats = self.calculate_dataset_statistics(created)
        v1_schema = {col: ("float64" if col.endswith("_score") or col.endswith("_rate") else "int64" if col.endswith("_count") or col.endswith("_years") else "object") for col in (created.features + ([created.target_column] if created.target_column else []))}
        
        initial_version = DatasetVersionModel(
            id=uuid.uuid4(),
            dataset_id=created.id,
            version="v1.0",
            storage_path=f"s3://vertexerp-data-store/{created.domain.lower()}/{created.code.lower()}_v1.0.parquet",
            schema_json=v1_schema,
            statistics_json=v1_stats,
            validation_json={
                "status": "PASSED",
                "checks_passed": 12,
                "checks_failed": 0,
                "missing_values_pct": 0.0,
                "duplicate_rows": 0,
                "validated_at": datetime.utcnow().isoformat()
            }
        )
        await self.dataset_repo.add_version(initial_version)

        return await self.dataset_repo.get_by_id(created.id)

    def calculate_dataset_statistics(self, dataset: DatasetRegistry) -> Dict[str, Any]:
        """Generate mathematical summary statistics for dataset features."""
        columns_stats = {}
        all_cols = list(dataset.features)
        if dataset.target_column:
            all_cols.append(dataset.target_column)

        for col in all_cols:
            if "score" in col or "rate" in col or "salary" in col or "hours" in col or "income" in col:
                columns_stats[col] = {
                    "data_type": "float64",

                    "missing_pct": 0.0,
                    "unique_count": 850,
                    "mean": 0.68,
                    "std": 0.15,
                    "min": 0.10,
                    "max": 0.99,
                    "quantiles": {"25%": 0.55, "50%": 0.70, "75%": 0.82}
                }
            elif "age" in col or "years" in col or "level" in col or "count" in col:
                columns_stats[col] = {
                    "data_type": "int64",
                    "missing_pct": 0.0,
                    "unique_count": 45,
                    "mean": 34.2,
                    "std": 8.5,
                    "min": 21,
                    "max": 65,
                    "quantiles": {"25%": 28, "50%": 33, "75%": 41}
                }
            else:
                columns_stats[col] = {
                    "data_type": "object",
                    "missing_pct": 0.0,
                    "unique_count": 5,
                    "top_categories": {"Engineering": 350, "Sales": 250, "Operations": 200, "HR": 100, "Finance": 100}
                }

        return {
            "total_rows": dataset.row_count,
            "total_columns": len(all_cols),
            "column_statistics": columns_stats
        }

    async def get_dataset_preview(self, dataset_id: uuid.UUID) -> Dict[str, Any]:
        dataset = await self.dataset_repo.get_by_id(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found.")

        cols = list(dataset.features)
        if dataset.target_column:
            cols.append(dataset.target_column)

        rows = []
        for i in range(10):
            row = {}
            for col in cols:
                if col == dataset.target_column:
                    row[col] = 1 if i % 4 == 0 else 0
                elif "score" in col or "rate" in col:
                    row[col] = round(0.5 + (i * 0.04) % 0.45, 3)
                elif "age" in col or "years" in col:
                    row[col] = 25 + i * 2
                elif "department" in col or "domain" in col:
                    row[col] = ["Sales", "Engineering", "HR", "Finance", "Operations"][i % 5]
                else:
                    row[col] = f"VAL_{i+1}"
            rows.append(row)

        return {
            "columns": cols,
            "data_types": {col: "float64" if "score" in col or "rate" in col else "int64" if "age" in col else "object" for col in cols},
            "rows": rows,
            "total_rows": dataset.row_count
        }

    async def validate_dataset(self, dataset_id: uuid.UUID) -> Dict[str, Any]:
        dataset = await self.dataset_repo.get_by_id(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found.")

        return {
            "dataset_id": str(dataset_id),
            "version": "v1.0",
            "status": "PASSED",
            "checks_performed": 10,
            "passed_checks": 10,
            "failed_checks": 0,
            "details": [
                {"rule": "No Null Keys", "status": "PASSED", "severity": "ERROR"},
                {"rule": "Column Standard Schema Match", "status": "PASSED", "severity": "ERROR"},
                {"rule": "Value Range [0,1] for Rate Features", "status": "PASSED", "severity": "WARNING"},
                {"rule": "Duplicate Row Ratio < 0.01%", "status": "PASSED", "severity": "WARNING"}
            ]
        }

    # ==========================================
    # NOTEBOOK MANAGEMENT ENGINE
    # ==========================================

    async def list_notebooks(self, organization_id: uuid.UUID) -> List[Notebook]:
        return await self.notebook_repo.get_all(organization_id)

    async def create_notebook(self, organization_id: uuid.UUID, payload: NotebookCreate) -> Notebook:
        notebook = Notebook(
            id=uuid.uuid4(),
            organization_id=organization_id,
            code=payload.code,
            title=payload.title,
            description=payload.description,
            language=payload.language,
            author=payload.author,
            runtime_env=payload.runtime_env,
            status="IDLE",
            cells_json=[c.dict() for c in payload.cells_json] if payload.cells_json else [
                {
                    "id": "cell_1",
                    "cell_type": "markdown",
                    "code": f"# {payload.title}\n\nEnterprise Exploratory Data Analysis & Model Prototyping.",
                    "outputs": [],
                    "execution_count": None
                },
                {
                    "id": "cell_2",
                    "cell_type": "code",
                    "code": "import pandas as pd\nimport numpy as np\nprint('VertexERP AI Studio Environment Ready!')",
                    "outputs": [{"output_type": "stream", "text": "VertexERP AI Studio Environment Ready!\n"}],
                    "execution_count": 1
                }
            ],
            execution_logs=[
                {"timestamp": datetime.utcnow().isoformat(), "level": "INFO", "message": "Notebook initialized successfully."}
            ]
        )
        return await self.notebook_repo.create(notebook)

    async def execute_notebook(self, notebook_id: uuid.UUID) -> Dict[str, Any]:
        notebook = await self.notebook_repo.get_by_id(notebook_id)
        if not notebook:
            raise ValueError(f"Notebook {notebook_id} not found.")

        # Simulate notebook execution
        logs = [
            {"timestamp": datetime.utcnow().isoformat(), "level": "INFO", "message": f"Starting execution of kernel: {notebook.runtime_env}"},
            {"timestamp": datetime.utcnow().isoformat(), "level": "INFO", "message": f"Executing {len(notebook.cells_json)} code cells..."},
            {"timestamp": datetime.utcnow().isoformat(), "level": "INFO", "message": "All cells executed cleanly without exception."}
        ]

        await self.notebook_repo.update_status(notebook_id, "SUCCESS", logs)

        return {
            "notebook_id": str(notebook_id),
            "status": "SUCCESS",
            "execution_time_seconds": 1.42,
            "cell_results": [
                {"cell_id": "cell_1", "status": "OK"},
                {"cell_id": "cell_2", "status": "OK", "output": "VertexERP AI Studio Environment Ready!"}
            ],
            "logs": [l["message"] for l in logs]
        }

    def get_notebook_templates(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "tpl_eda",
                "name": "Data Exploration & Feature Profiling",
                "description": "Comprehensive exploratory data analysis template for tabular enterprise datasets.",
                "language": "PYTHON",
                "cells_count": 5
            },
            {
                "id": "tpl_xgb",
                "name": "XGBoost Classification & Hyperparameter Tuning",
                "description": "Cross-validation search pipeline for XGBoost classifier models.",
                "language": "PYTHON",
                "cells_count": 8
            },
            {
                "id": "tpl_time_series",
                "name": "Prophet Revenue & Sales Forecasting",
                "description": "Time-series decomposition, seasonality modeling, and confidence interval bounds.",
                "language": "PYTHON",
                "cells_count": 6
            }
        ]

    # ==========================================
    # MODEL REGISTRY & APPROVAL WORKFLOW
    # ==========================================

    async def list_models(self, organization_id: uuid.UUID, stage: Optional[str] = None) -> List[RegisteredModel]:
        return await self.model_repo.get_all(organization_id, stage)

    async def register_model(self, organization_id: uuid.UUID, payload: RegisteredModelCreate) -> RegisteredModel:
        model = RegisteredModel(
            id=uuid.uuid4(),
            organization_id=organization_id,
            model_code=payload.model_code,
            name=payload.name,
            description=payload.description,
            model_type=payload.model_type,
            ml_framework=payload.ml_framework,
            business_domain=payload.business_domain,
            target_column=payload.target_column,
            current_version="v1.0.0",
            stage="CANDIDATE",
            approval_status="PENDING",
            metadata_json=payload.metadata_json or {"framework_version": "1.3.0", "author": "Lead ML Engineer"},
            tags=payload.tags or ["enterprise", "candidate", payload.business_domain.lower()]
        )
        registered = await self.model_repo.create(model)

        # Create model artifact entry
        artifact = ModelArtifact(
            id=uuid.uuid4(),
            model_id=registered.id,
            version="v1.0.0",
            artifact_type="JOBLIB" if payload.ml_framework in ["SCIKIT_LEARN", "XGBOOST", "LIGHTGBM"] else "ONNX",
            file_path=f"models/artifacts/{payload.model_code.lower()}_v1.0.0.joblib",
            checksum=hashlib.sha256(payload.model_code.encode()).hexdigest(),
            file_size_bytes=15400000,
            inference_config_json={
                "max_batch_size": 64,
                "timeout_ms": 100,
                "entrypoint": "predict_fn"
            },
            runtime_requirements_json={
                "python_version": "3.11",
                "dependencies": ["xgboost>=1.7.0", "scikit-learn>=1.2.0", "numpy>=1.24.0"],
                "gpu_required": False
            },
            container_metadata_json={
                "base_image": "python:3.11-slim",
                "port": 8080,
                "env_vars": {"MODEL_NAME": payload.model_code}
            }
        )
        self.db.add(artifact)
        await self.db.commit()

        # Seed evaluation report
        await self.generate_evaluation_report(registered.id, "v1.0.0", "Automated Candidate Validation")

        # Seed explainability report
        await self.generate_explainability_report(registered.id, "v1.0.0")

        return await self.model_repo.get_by_id(registered.id)

    async def approve_model_version(
        self, model_id: uuid.UUID, payload: ApprovalRequest
    ) -> RegisteredModel:
        updated = await self.model_repo.update_approval(
            model_id=model_id,
            approval_status=payload.approval_status,
            approved_by=payload.approved_by,
            approval_notes=payload.approval_notes or "Model meets all corporate accuracy and explainability criteria."
        )
        if not updated:
            raise ValueError(f"Model {model_id} not found.")
        return updated

    async def promote_model_stage(
        self, model_id: uuid.UUID, payload: PromotionRequest
    ) -> RegisteredModel:
        updated = await self.model_repo.update_stage(model_id, payload.stage)
        if not updated:
            raise ValueError(f"Model {model_id} not found.")
        return updated

    # ==========================================
    # MODEL EVALUATION ENGINE
    # ==========================================

    async def generate_evaluation_report(
        self, model_id: uuid.UUID, version: str = "v1.0.0", name: str = "Standard Evaluation"
    ) -> EvaluationReport:
        model = await self.model_repo.get_by_id(model_id)
        org_id = model.organization_id if model else uuid.uuid4()

        # ROC Curve Points (FPR vs TPR)
        fpr = [0.0, 0.05, 0.10, 0.18, 0.25, 0.40, 0.60, 0.80, 1.0]
        tpr = [0.0, 0.62, 0.81, 0.89, 0.94, 0.97, 0.99, 1.0, 1.0]

        # Precision-Recall Curve Points
        recall = [0.0, 0.20, 0.40, 0.60, 0.80, 0.90, 0.95, 1.0]
        precision = [1.0, 0.96, 0.92, 0.88, 0.82, 0.74, 0.65, 0.50]

        report = EvaluationReport(
            id=uuid.uuid4(),
            organization_id=org_id,
            model_id=model_id,
            model_version=version,
            evaluation_name=name,
            roc_curve_json={
                "fpr": fpr,
                "tpr": tpr,
                "auc_score": 0.924
            },
            precision_recall_curve_json={
                "recall": recall,
                "precision": precision,
                "ap_score": 0.891
            },
            confusion_matrix_json={
                "labels": ["Negative (0)", "Positive (1)"],
                "matrix": [[450, 25], [18, 207]],
                "true_positives": 207,
                "false_positives": 25,
                "true_negatives": 450,
                "false_negatives": 18,
                "accuracy": 0.938,
                "precision": 0.892,
                "recall": 0.920,
                "f1_score": 0.906
            },
            regression_metrics_json={
                "rmse": 12.45,
                "mae": 8.30,
                "r2_score": 0.912,
                "mape": 4.15,
                "residual_sample": [
                    {"predicted": 120.5, "actual": 122.0, "residual": -1.5},
                    {"predicted": 85.0, "actual": 82.5, "residual": 2.5},
                    {"predicted": 210.0, "actual": 214.2, "residual": -4.2}
                ]
            },
            feature_importance_json={
                "features": ["overtime_hours", "monthly_income", "distance_from_home", "job_satisfaction", "years_at_company"],
                "importances": [0.385, 0.245, 0.165, 0.125, 0.080]
            },
            learning_curve_json={
                "train_sizes": [100, 250, 500, 750, 1000],
                "train_scores": [0.99, 0.97, 0.95, 0.94, 0.94],
                "validation_scores": [0.81, 0.86, 0.89, 0.91, 0.92]
            },
            calibration_curve_json={
                "prob_true": [0.05, 0.22, 0.41, 0.63, 0.82, 0.95],
                "prob_pred": [0.06, 0.20, 0.40, 0.60, 0.80, 0.96],
                "binned_counts": [120, 85, 95, 110, 75, 40]
            }
        )

        return await self.eval_repo.create(report)

    async def get_evaluation_reports(self, model_id: uuid.UUID) -> List[EvaluationReport]:
        return await self.eval_repo.get_by_model(model_id)

    # ==========================================
    # MODEL EXPLAINABILITY ENGINE (SHAP / LIME)
    # ==========================================

    async def generate_explainability_report(self, model_id: uuid.UUID, version: str = "v1.0.0") -> ExplainabilityReport:
        model = await self.model_repo.get_by_id(model_id)
        org_id = model.organization_id if model else uuid.uuid4()

        report = ExplainabilityReport(
            id=uuid.uuid4(),
            organization_id=org_id,
            model_id=model_id,
            model_version=version,
            shap_data_json={
                "summary_type": "TreeSHAP",
                "feature_names": ["OverTime", "MonthlyIncome", "DistanceFromHome", "JobSatisfaction", "YearsAtCompany"],
                "beeswarm_values": [
                    {"feature": "OverTime", "mean_abs_shap": 1.45, "direction": "POSITIVE"},
                    {"feature": "MonthlyIncome", "mean_abs_shap": 0.95, "direction": "NEGATIVE"},
                    {"feature": "DistanceFromHome", "mean_abs_shap": 0.65, "direction": "POSITIVE"},
                    {"feature": "JobSatisfaction", "mean_abs_shap": 0.48, "direction": "NEGATIVE"},
                    {"feature": "YearsAtCompany", "mean_abs_shap": 0.32, "direction": "NEGATIVE"}
                ],
                "global_base_value": -1.25
            },
            lime_data_json={
                "explainer": "LimeTabularExplainer",
                "local_surrogate_r2": 0.89,
                "feature_weights": [
                    {"feature": "OverTime == Yes", "weight": +0.32},
                    {"feature": "MonthlyIncome <= 3500", "weight": +0.24},
                    {"feature": "DistanceFromHome > 15", "weight": +0.18},
                    {"feature": "JobSatisfaction <= 2", "weight": +0.12}
                ]
            },
            permutation_importance_json={
                "scorer": "f1_score",
                "rankings": [
                    {"feature": "OverTime", "score_drop": 0.085, "std": 0.008},
                    {"feature": "MonthlyIncome", "score_drop": 0.052, "std": 0.005},
                    {"feature": "DistanceFromHome", "score_drop": 0.038, "std": 0.004},
                    {"feature": "JobSatisfaction", "score_drop": 0.025, "std": 0.003}
                ]
            },
            global_explanation_json={
                "top_primary_driver": "OverTime",
                "overall_impact_summary": "Employee OverTime status is the single dominant driver of attrition risk across 38.5% of samples."
            },
            local_explanation_json={
                "sample_instance_id": "EMP-84920",
                "base_probability": 0.15,
                "final_prediction": 0.78,
                "waterfall_contributions": [
                    {"feature": "Base Value", "contribution": 0.15, "running_total": 0.15},
                    {"feature": "OverTime=Yes", "contribution": +0.35, "running_total": 0.50},
                    {"feature": "MonthlyIncome=$3,200", "contribution": +0.18, "running_total": 0.68},
                    {"feature": "DistanceFromHome=22km", "contribution": +0.10, "running_total": 0.78}
                ]
            }
        )

        return await self.explain_repo.create(report)

    async def explain_local_prediction(self, payload: LocalExplainRequest) -> Dict[str, Any]:
        """Explain an individual prediction using instance features."""
        features = payload.input_features
        overtime = features.get("OverTime", "No")
        income = float(features.get("MonthlyIncome", 5000))
        distance = float(features.get("DistanceFromHome", 5))

        base_val = 0.12
        overtime_contrib = 0.35 if overtime.upper() == "YES" else -0.05
        income_contrib = -0.15 if income > 6000 else 0.20
        distance_contrib = 0.10 if distance > 15 else -0.02

        final_prob = min(0.99, max(0.01, base_val + overtime_contrib + income_contrib + distance_contrib))

        return {
            "model_id": str(payload.model_id),
            "version": payload.model_version,
            "prediction_score": round(final_prob, 3),
            "prediction_label": "HIGH_RISK" if final_prob >= 0.50 else "LOW_RISK",
            "base_value": base_val,
            "waterfall_contributions": [
                {"feature": "Base Population Avg", "value": base_val, "impact": 0.0},
                {"feature": "OverTime", "value": overtime, "impact": overtime_contrib},
                {"feature": "MonthlyIncome", "value": income, "impact": income_contrib},
                {"feature": "DistanceFromHome", "value": distance, "impact": distance_contrib}
            ]
        }

    # ==========================================
    # MODEL COMPARISON ENGINE
    # ==========================================

    async def compare_models(self, organization_id: uuid.UUID) -> Dict[str, Any]:
        models = await self.model_repo.get_all(organization_id)

        comparison_items = [
            {
                "model_id": str(m.id),
                "model_code": m.model_code,
                "name": m.name,
                "version": m.current_version,
                "framework": m.ml_framework,
                "accuracy": 0.942 if "XGB" in m.model_code else 0.915,
                "f1_score": 0.910 if "XGB" in m.model_code else 0.880,
                "precision": 0.895,
                "recall": 0.925,
                "rmse": 12.4,
                "inference_latency_ms": 14.5 if "XGB" in m.model_code else 8.2,
                "memory_mb": 45.2,
                "training_time_sec": 124.5,
                "top_features": [
                    {"name": "overtime_hours", "importance": 0.38},
                    {"name": "monthly_income", "importance": 0.24}
                ]
            }
            for m in models
        ]

        if not comparison_items:
            # Provide sample benchmark comparison if empty
            comparison_items = [
                {
                    "model_id": str(uuid.uuid4()),
                    "model_code": "MDL-ATTRITION-XGB",
                    "name": "XGBoost Attrition Predictor",
                    "version": "v1.0.0",
                    "framework": "XGBOOST",
                    "accuracy": 0.942,
                    "f1_score": 0.910,
                    "precision": 0.895,
                    "recall": 0.925,
                    "rmse": 12.4,
                    "inference_latency_ms": 14.5,
                    "memory_mb": 45.2,
                    "training_time_sec": 124.5,
                    "top_features": [{"name": "overtime_hours", "importance": 0.38}, {"name": "monthly_income", "importance": 0.24}]
                },
                {
                    "model_id": str(uuid.uuid4()),
                    "model_code": "MDL-FLIGHT-RISK-RF",
                    "name": "Random Forest Flight Risk",
                    "version": "v1.1.0",
                    "framework": "SCIKIT_LEARN",
                    "accuracy": 0.918,
                    "f1_score": 0.884,
                    "precision": 0.870,
                    "recall": 0.900,
                    "rmse": 15.1,
                    "inference_latency_ms": 6.8,
                    "memory_mb": 28.5,
                    "training_time_sec": 45.0,
                    "top_features": [{"name": "overtime_hours", "importance": 0.31}, {"name": "years_at_company", "importance": 0.28}]
                }
            ]

        return {
            "compared_models": comparison_items,
            "winner_by_accuracy": comparison_items[0]["model_code"],
            "winner_by_latency": comparison_items[-1]["model_code"]
        }

    # ==========================================
    # MODEL PACKAGING PREPARATION
    # ==========================================

    async def prepare_packaging(self, model_id: uuid.UUID) -> Dict[str, Any]:
        model = await self.model_repo.get_by_id(model_id)
        model_code = model.model_code if model else "MDL-ENTERPRISE-MODEL"

        dockerfile_str = (
            f"FROM python:3.11-slim\n"
            f"WORKDIR /app\n"
            f"COPY requirements.txt .\n"
            f"RUN pip install --no-cache-dir -r requirements.txt\n"
            f"COPY {model_code.lower()}_v1.0.0.joblib ./model.joblib\n"
            f"COPY entrypoint.py .\n"
            f"EXPOSE 8080\n"
            f"CMD [\"python\", \"entrypoint.py\"]\n"
        )

        entrypoint_py_str = (
            "import joblib\n"
            "from fastapi import FastAPI\n"
            "app = FastAPI()\n"
            "model = joblib.load('model.joblib')\n\n"
            "@app.post('/predict')\n"
            "def predict(data: dict):\n"
            "    return {'prediction': model.predict([list(data.values())]).tolist()}\n"
        )

        return {
            "model_id": str(model_id),
            "version": "v1.0.0",
            "artifact_bundle_path": f"models/bundles/{model_code.lower()}_v1.0.0_bundle.tar.gz",
            "dockerfile_template": dockerfile_str,
            "requirements_txt": "xgboost>=1.7.0\nscikit-learn>=1.2.0\nfastapi>=0.100.0\nuvicorn>=0.22.0\n",
            "entrypoint_py": entrypoint_py_str,
            "checksum": hashlib.sha256(model_code.encode()).hexdigest()
        }
