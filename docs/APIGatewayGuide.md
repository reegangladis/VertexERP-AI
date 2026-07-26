# API Gateway Guide — VertexERP AI

## Overview
The **API Gateway** acts as the single enterprise entry point for external API consumers, microservices, and third-party partner integrations.

---

## Core Capabilities

### 1. Dynamic Routing & API Versioning
Routes are mapped to backend services with version prefixes:
- `/v1/erp/sync` -> `SAP ERP Connector`
- `/v1/crm/contacts` -> `Salesforce CRM Connector`
- `/v2/analytics/reports` -> `BI Analytics Engine`

### 2. Token Bucket Rate Limiting
Rate limiting is evaluated per API key or client identifier using a sliding window algorithm.
- Default limit: 50 requests/sec (RPS), 1000 requests/min (RPM)
- Exceeded rate limits return HTTP `429 Too Many Requests`.

### 3. Response Caching
High-frequency GET queries support TTL-based caching.
- Cache keys: `MD5(route_path + query_params)`
- Configurable TTL (e.g. 60s, 300s)

### 4. API Key Verification & OAuth 2.0
- API keys format: `vx_live_<random_bytes>`
- Hashed storage using SHA-256
- Scoped RBAC permissions: `read`, `write`, `connectors:execute`, `admin`
- Client credentials OAuth 2.0 token endpoint `/api/v1/integration/auth/oauth/token`

---

## API Endpoints

- `POST /api/v1/integration/gateway/route`: Resolve URI path and apply policies
- `POST /api/v1/integration/gateway/verify-key`: Verify API Key signature and scopes
- `GET /api/v1/integration/gateway/rate-limit-check`: Check client RPS budget
- `GET /api/v1/integration/gateway/cache`: Retrieve cached response payload
- `GET /api/v1/integration/analytics/summary`: Aggregate Gateway traffic metrics
