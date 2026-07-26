# Enterprise ML Studio Guide — VertexERP AI

## Overview
The **Enterprise ML Studio** provides a unified workbench for data scientists and ML engineers to explore datasets, execute interactive notebooks, track hyperparameter experiments, monitor training queue jobs, evaluate diagnostic metrics, manage model approval lifecycles, inspect SHAP/LIME explainability, and prepare deployment container packaging.

---

## Key Studio Modules

1. **Dataset Explorer & Registry**:
   - Dataset catalog with format support (Parquet, CSV, JSON, SQL).
   - Versioning (`v1.0`, `v1.1`) and data lineage graph tracking.
   - Column statistics calculation (missing ratios, distributions, min, max, mean, std, unique counts).
   - Data quality rules validation (missing values check, schema mismatch, duplicate detection).
   - Head rows data preview table.

2. **Interactive Notebook Registry**:
   - Notebook catalog supporting Python, SQL, and R kernel execution environments.
   - Notebook execution simulator with cell output tracking and stdout log console.
   - Pre-built data science templates (Data Exploration, XGBoost Tuning, Prophet Time-Series Analysis).

3. **Experiment Tracker**:
   - Multi-trial hyperparameter run comparisons.
   - Track parameters (`learning_rate`, `max_depth`, `n_estimators`, `subsample`, `batch_size`).
   - Side-by-side metric matrix (Accuracy, Loss, Precision, Recall, F1, ROC AUC, RMSE).
   - Visual progress bars comparing ROC AUC across trial iterations.

4. **Training Jobs Manager**:
   - Real-time training queue status management (`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `RETRYING`).
   - Failed worker job retry triggers.
   - Stdout streaming log console.

5. **Model Registry & Approval Workflow**:
   - Centralized model version catalog (`v1.0.0`, `v1.1.0`).
   - Stage progression (`DRAFT` → `CANDIDATE` → `APPROVED` → `STAGING` → `PRODUCTION` → `ARCHIVED`).
   - Formal sign-off approval workflow (`APPROVED`, `REJECTED`, reviewer sign-off, approval notes).

6. **Model Evaluation Reports**:
   - Receiver Operating Characteristic (ROC) curve with AUC score.
   - Precision-Recall (PR) curve with Average Precision (AP).
   - 2x2 & NxN Confusion Matrix visualizer (TP, FP, TN, FN).
   - Feature Importance weight rankings.
   - Learning curves (train vs validation loss convergence).
   - Probability calibration curve placeholder.

7. **Explainability Dashboard (XAI)**:
   - TreeSHAP summary and beeswarm plots.
   - LIME local linear surrogate decision rules.
   - Permutation importance rankings.
   - Interactive per-instance prediction waterfall explainer.

8. **Model Comparison & Benchmark**:
   - Multi-model comparative benchmark matrix.
   - Winner highlight badges for Highest Accuracy and Lowest Inference Latency (ms).

9. **Packaging Preparation**:
   - Export artifact bundle metadata (`.tar.gz`, SHA256 checksum).
   - Dockerfile template generator (`python:3.11-slim`).
   - `requirements.txt` and `entrypoint.py` inference entrypoint script generator.
