# Model Registry & Approval Workflow Guide — VertexERP AI

## Overview
The **Model Registry** in **VertexERP AI** serves as the authoritative single source of truth for all machine learning models across HR, CRM, Finance, Inventory, and Manufacturing domains. It governs the entire model lifecycle from draft candidate models to production deployment and archiving.

---

## Lifecycle Stages
1. **DRAFT**: Initial experimental prototype.
2. **CANDIDATE**: Trained model version submitted for validation.
3. **APPROVED**: Passed formal sign-off review by Principal AI Architect / Lead ML Engineer.
4. **STAGING**: Deployed to staging environment for integration testing.
5. **PRODUCTION**: Approved and active for live real-time and batch predictions.
6. **ARCHIVED**: Soft-deleted or deprecated model version.

---

## Approval Workflow Protocol
- **Submit Candidate**: When a training job produces a candidate model with target metrics, it is registered under `CANDIDATE` stage with `PENDING` approval status.
- **Review**: Reviewers inspect the Evaluation Report (ROC AUC, Confusion Matrix, Feature Importance) and Explainability Report (SHAP/LIME).
- **Approval Sign-off**: The reviewer submits a formal sign-off request via `POST /api/v1/ml-studio/models/{id}/approve` with approval status (`APPROVED` or `REJECTED`) and reviewer notes.
- **Stage Promotion**: Approved models can be promoted to `PRODUCTION` via `POST /api/v1/ml-studio/models/{id}/promote`.
