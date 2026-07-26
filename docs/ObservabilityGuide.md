# Observability & Distributed Tracing Guide - VertexERP AI

This guide describes how to record, track, and analyze logs and request traces across VertexERP AI microservices.

## Structured Logging

Centralized logs contain unified context parameters mapping transaction events to tenant and request environments:

```json
{
  "timestamp": "2026-07-26T12:00:00Z",
  "service_name": "rest-api",
  "log_level": "ERROR",
  "message": "Failed invoice database validation roundtrip",
  "request_id": "req-9c8a7f2e",
  "correlation_id": "corr-4a3b2c1d",
  "structured_data": {
    "organization_id": "d3b07384-d113-4ec6-a5d9-482d2a74e1d9",
    "invoice_code": "INV-2026-004",
    "db_code": "504"
  }
}
```

---

## Distributed Trace Spans

Trace spans correlate multiple microservice steps within a transaction:

1. **Transaction Trigger**: Call hits API Gateway, injecting a unique `trace_id` header `X-Request-ID`.
2. **Context Propagation**: The gateway passes `trace_id` to services (e.g. Finance, HR, AI Copilot).
3. **Span Records**: Each service creates a nested `TraceSpan` identifying parent-child relationships using `parent_span_id`.

### Trace Span Schema Example

- **Endpoint**: `POST /api/v1/observability/traces`
- **Payload**:
```json
{
  "trace_id": "tr-4a3b2c1d",
  "span_id": "sp-finance-db-query",
  "parent_span_id": "sp-api-gateway-handler",
  "name": "SQL query invoices",
  "service_name": "finance-service",
  "start_time": "2026-07-26T12:00:00.123Z",
  "end_time": "2026-07-26T12:00:00.285Z",
  "duration_ms": 162.0,
  "status": "success",
  "attributes": {
    "table": "invoices",
    "db_pool_size": 20
  }
}
```
