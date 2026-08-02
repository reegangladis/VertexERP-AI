# Model Deployment Guide

This guide details the deployment routing strategies supported by the VertexERP AI MLOps Platform.

---

## 1. Supported Deployment Strategies

| Strategy | Description | Benefits | Use Case |
| :--- | :--- | :--- | :--- |
| **Blue-Green** | Maintains two identical physical deployments. Blue is active, Green contains the new candidate version. Shift is atomic. | Zero downtime, instant rollback. | Major release upgrades. |
| **Canary** | Routes a minor traffic percentage (e.g. 5-15%) to the new champion version while baseline handles the rest. | Real-world validation with low risk. | High-volume critical APIs. |
| **Shadow** | Routes 100% of production traffic to both active baseline and candidate, but discards candidate response outputs. | Latency & load verification under real load. | Performance testing new models. |

---

## 2. Shift and Promotion Procedures

### Step 1: Request Promotion
Submit a promotion approval request specifying the `model_version_id`, target environment (`STAGING` or `PRODUCTION`), and compliance logs.

### Step 2: Governance Review
The AI Architect validates features drift history, ROC-AUC metric validations, and security signatures in the governance queue.

### Step 3: Shift Traffic
For Canary strategies, slowly increment the canary slider from `5%` to `100%` in the **Deployment Center** UI.

---

## 3. Emergency Rollback

If validation performance metrics degrade, error rates exceed 5.0%, or CPU load metrics alerts trigger:
1. Open the **Deployment Center** panel.
2. Select the degraded endpoint and click **Rollback**.
3. Specify the target stable Version UUID and click **Initiate Rollback**.
4. The router atomically shifts `100%` traffic split back to the stable baseline, and records rollback notes in the `deployment_history` audit trail.
