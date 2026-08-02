# Enterprise ML Inference Guide

## Overview
The **Inference Engine** supports low-latency Real-Time Prediction APIs, Batch Prediction APIs, Prediction History tracking, and Ground Truth Feedback logging.

---

## Real-Time Prediction API
`POST /api/v1/ml/inference/predict`

**Request Payload:**
```json
{
  "business_module": "attrition",
  "input_data": {
    "tenure_months": 24,
    "satisfaction_score": 2.1,
    "overtime_hours": 20,
    "salary_percentile": 40
  }
}
```

**Response Payload:**
```json
{
  "id": "7f8c9b21-4d32-4e12-89a1-0294e75a1b32",
  "prediction_type": "REALTIME",
  "business_module": "attrition",
  "input_data_json": { ... },
  "output_data_json": {
    "attrition_probability": 0.724,
    "predicted_turnover_risk": "HIGH"
  },
  "confidence_score": 0.94,
  "latency_ms": 11.2,
  "status": "SUCCESS"
}
```

---

## Batch Prediction API
`POST /api/v1/ml/inference/predict-batch`

Executes high-throughput batch prediction vector requests and logs predictions to history.

---

## Ground Truth Feedback Loop
`POST /api/v1/ml/inference/feedback`

Submit post-hoc actual values to monitor model drift and accuracy over time:
```json
{
  "prediction_id": "7f8c9b21-4d32-4e12-89a1-0294e75a1b32",
  "actual_value": 1,
  "feedback_score": 1.0,
  "evaluation_status": "CORRECT"
}
```
