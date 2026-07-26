# Monitoring Guide - VertexERP AI

This guide describes how to configure, record, and inspect raw system metrics in the VertexERP AI Monitoring & Observability Platform.

## Core Metric Telemetry

The platform collects real-time system performance data to diagnose latencies and resource usage:

| Metric Name | Type | Unit | Description |
|---|---|---|---|
| `cpu_usage` | `gauge` | `%` | Percentage load aggregated across CPU cores. |
| `memory_usage` | `gauge` | `%` | Percentage of active RAM memory allocation. |
| `api_latency` | `histogram` | `ms` | HTTP roundtrip delays for request processing. |
| `database_performance` | `histogram` | `ms` | Transaction execution duration on PostgreSQL tables. |
| `token_usage` | `counter` | tokens | Accumulated LLM prompt & completion tokens consumed. |
| `rag_retrieval` | `histogram` | `ms` | Search similarity latency on vector indexes. |

---

## Metric Schema & API Specifications

### Submit System Metric

- **Endpoint**: `POST /api/v1/observability/metrics`
- **Headers**:
  - `Content-Type: application/json`
  - `Authorization: Bearer <JWT_TOKEN>`
- **Payload Schema**:
```json
{
  "metric_name": "api_latency",
  "metric_type": "histogram",
  "value": 145.2,
  "labels": {
    "service": "finance-service",
    "endpoint": "/invoices",
    "method": "GET"
  }
}
```

### Query Metric History

- **Endpoint**: `GET /api/v1/observability/metrics`
- **Parameters**:
  - `metric_name` (optional): Filter by name.
  - `duration_minutes` (optional): Number of minutes to look back (default: 60).
- **Headers**:
  - `Authorization: Bearer <JWT_TOKEN>`
