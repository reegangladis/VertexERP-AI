# ETL / ELT Pipelines Guide - VertexERP AI

## Pipeline Engine Overview
VertexERP AI includes an enterprise ETL/ELT pipeline engine responsible for extracting data from transactional source systems, executing transformations, and loading into Data Lake zones and Data Warehouse fact/dimension tables.

---

## Key Pipeline Features

1. **Incremental & Full Loads**:
   - Supports change-data-capture (CDC) incremental loads for high-frequency streaming.
   - Supports periodic full refresh loads for general ledger rollups.

2. **Scheduling Architecture**:
   - Standard 5-field cron scheduling format (`0 * * * *`, `15 * * * *`, etc.).
   - Support for `REALTIME`, `HOURLY`, `DAILY`, `WEEKLY`, and `MANUAL` execution frequencies.

3. **Retry Mechanism & Logging**:
   - Configurable retry limit per pipeline job (default 3 retries).
   - Execution state tracking in `etl_jobs`, `etl_runs`, and detailed phase logs in `pipeline_logs`.

---

## API Endpoints

- `GET /api/v1/data-engineering/etl-jobs`: List pipeline job definitions.
- `POST /api/v1/data-engineering/etl-jobs`: Create a new pipeline job.
- `POST /api/v1/data-engineering/etl-jobs/{id}/run`: Manually trigger pipeline execution.
- `GET /api/v1/data-engineering/runs/{id}/logs`: Fetch execution logs for a pipeline run.
