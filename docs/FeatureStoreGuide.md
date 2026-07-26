# Feature Store Guide - VertexERP AI (AI-Ready Architecture)

## Overview
The **VertexERP AI Feature Store** serves as the central registry for machine learning features, time-series aggregations, and entity embeddings prepared for future AI/ML pipelines, demand forecasting, recommendation engines, and LLM RAG pipelines.

---

## Architecture Components

1. **Feature Groups (`feature_groups`)**:
   - Logical group of features centered around an entity key (e.g. `customer_id`, `product_id`, `employee_id`).
   - Maps offline batch tables (e.g. `curated_customer_features`) with online Redis key-value caches.

2. **Feature Registry (`feature_registry`)**:
   - Individual feature definitions, data types (`FLOAT`, `INT`, `VECTOR`, `STRING`), aggregation windows (`7D`, `30D`, `90D`), and SQL transformations.
   - Extension attribute `ml_feature_type` (`NUMERICAL`, `CATEGORICAL`, `EMBEDDING_PLACEHOLDER`) for seamless future AI consumption.

3. **Offline & Online Stores**:
   - **Offline Store**: Historical Parquet datasets for ML model training.
   - **Online Store**: Low-latency cache architecture placeholder for real-time inference lookup.

---

## API Endpoints

- `GET /api/v1/data-engineering/feature-groups`: List registered feature groups.
- `POST /api/v1/data-engineering/feature-groups`: Register a new feature group.
- `POST /api/v1/data-engineering/features`: Register an individual feature within a feature group.
