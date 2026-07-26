# Model Explainability (XAI) Guide — VertexERP AI

## Overview
VertexERP AI enforces Explainable AI (XAI) standards to ensure all automated predictions across HR attrition, customer churn, fraud detection, and quality defect predictors are interpretable, audited, and compliant with enterprise governance standards.

---

## Explainability Techniques Supported

1. **TreeSHAP & KernelSHAP**:
   - Calculates exact Shapley additive explanations for tree-based models (XGBoost, LightGBM, CatBoost, Random Forest).
   - Generates mean absolute SHAP feature rankings (`|mean(SHAP)|`) and summary beeswarm plot datasets.

2. **LIME (Local Interpretable Model-agnostic Explanations)**:
   - Fits an interpretable local linear surrogate model around individual sample instances.
   - Provides decision rules and boundary weights for local prediction predictions.

3. **Permutation Importance**:
   - Evaluates global feature importance by measuring metric score degradation (F1/AUC drop) when a feature column is randomly shuffled.

4. **Per-Instance Waterfall Explanations**:
   - Provides a step-by-step breakdown of how an individual instance's feature values push the baseline probability up or down to arrive at the final prediction score.
