# Enterprise Model Registry Guide

## Overview
The **Model Registry** is a centralized repository for managing the lifecycle of machine learning models and semantic versions in VertexERP AI.

---

## Model Registry Lifecycle Stages
1. **DRAFT**: Initial definition or unverified experimental candidate.
2. **CANDIDATE**: Automated training job result awaiting formal evaluation review.
3. **APPROVED**: Validated model version approved by ML Lead or Domain Expert.
4. **STAGING**: Staging environment testing status.
5. **PRODUCTION**: Active production version serving real-time and batch predictions.
6. **ARCHIVED**: Superseded or deprecated version.

---

## Approval Workflow Placeholder
Each candidate version requires explicit approval before promotion to `PRODUCTION`:
```json
POST /api/v1/ml/versions/{version_id}/approve
{
  "approved_by": "Lead Machine Learning Engineer"
}
```

---

## Versioning Scheme
Model versions follow Semantic Versioning (`vMAJOR.MINOR.PATCH`):
- **MAJOR**: Structural schema change or target variable modification.
- **MINOR**: Retrained iteration with new hyperparameter configuration or feature addition.
- **PATCH**: Hyperparameter tuning tweak or bug fix.
