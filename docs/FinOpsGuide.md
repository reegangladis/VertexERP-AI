# FinOps & Cloud Cost Optimization Guide — VertexERP AI

## Overview
This document covers multi-cloud cost allocation, resource right-sizing, budget alert thresholds, and savings optimization strategies.

---

## Cost Optimization Strategies

1. **Savings Plans & Reserved Instances**: Purchase 1-year or 3-year commitment plans for baseline EKS worker nodes and RDS database instances (Save 30-50%).
2. **Resource Right-Sizing**: Continuously adjust pod CPU/RAM requests based on Prometheus utilization metrics.
3. **Storage Lifecycle Management**: Transition backup snapshots older than 30 days to AWS S3 Glacier / Azure Archive Storage.
