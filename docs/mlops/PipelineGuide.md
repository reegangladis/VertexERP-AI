# MLOps Pipeline Guide

This guide documents the execution, structure, and customization rules for versioned MLOps Pipelines in VertexERP AI.

---

## 1. Pipeline Types

1. **Continuous Training (`TRAINING`)**: Fetches adaptation datasets, triggers hyperparameter grid search, and compiles model artifacts.
2. **Continuous Validation (`VALIDATION`)**: Evaluates a trained candidate against test data partitions to compute ROC-AUC, accuracy, and F1 scores.
3. **Continuous Deployment (`DEPLOYMENT` / `PROMOTION`)**: Packages model artifacts into portable containers and updates active routing configurations.
4. **Emergency Retraining (`RETRAINING`)**: Automatically triggered on feature/prediction drift, outputting a new candidate version.

---

## 2. CI/CD Artifact and Model Validation

All pipeline template runs trigger the following validations automatically:
- **Checksum Verification**: Validates artifact hashes to verify compilation safety.
- **Security Scans**: Scans libraries and models for known CVE exploits or malicious pickle injections.
- **Accuracy Benchmarks**: Enforces threshold gates (e.g., F1-score &gt;= baseline) before marking runs as COMPLETED.

---

## 3. Retrieving Logs and Telemetry

Pipeline logs are streamed to the DB:
1. Open the **Pipeline Manager** in the navigation panel.
2. Click **Console** on a target run.
3. The dark overlay display will stream console output details (e.g. training epoch details, signature scan flags, accuracy benchmarks validation scores).
