# VertexERP AI V2 — Remaining Non-Blocking Operational Risks

**Date:** 2026-09-13  
**Auditor:** Principal Site Reliability Engineering (SRE)  

---

## 1. Overview
All **P0 Blockers** and **P1 High Defects** have been resolved and verified with 100% test passes. The following operational risks are non-blocking for staging and initial production rollout, but must be monitored by SRE and Cloud Operations teams according to standard operating procedures.

---

## 2. Identified Operational Risks & Mitigations

### 1. External AI Provider Outages & Latency Spikes
- **Risk:** Upstream LLM providers (OpenAI, Anthropic, Google Gemini) can experience transient outages or rate limit throttles during peak hours.
- **Impact:** AI Copilot and RAG queries may return HTTP 504 / 502 to users.
- **Mitigation:** The AI Gateway implements timeout enforcement (`AI_REQUEST_TIMEOUT_SECONDS=30.0`), fallback error handling, and Prometheus error counters (`vertexerp_ai_requests_total{status="error"}`).
- **Action Required:** Operations must configure multi-provider failover routing in production environment configurations.

### 2. S3 Object Storage Lifecycle Rules & Storage Growth
- **Risk:** High volumes of uploaded PDF invoices, employee documents, and RAG knowledge base attachments will increase S3 bucket size over time.
- **Impact:** Increased object storage costs.
- **Mitigation:** The S3 storage client scopes objects under `tenants/{tenant_id}/{entity}/{YYYYMM}/` partitions.
- **Action Required:** Configure S3 Glacier lifecycle tiering for documents older than 365 days.

### 3. Continuous PostgreSQL WAL Archiving Configuration on Managed Database
- **Risk:** In Kubernetes-only environments without managed RDS / Cloud SQL, continuous point-in-time recovery requires an active WAL archiving daemon (`pgBackRest` or `wal-g`).
- **Impact:** Recovery point objective (RPO) is bounded by scheduled full database backups (e.g., 6 hours) rather than continuous sub-second streaming if WAL archiving is not configured on the self-hosted database instance.
- **Mitigation:** Encrypted snapshot backups with manifest verification and GFS retention are automated. Production deployments recommend AWS Aurora PostgreSQL or Google Cloud SQL with automated continuous WAL backup enabled.

### 4. High-Volume Redis Stream Consumer Group Scaling
- **Risk:** Spike in outbound integrations or asynchronous bulk PDF report generation could temporarily increase Redis Stream consumer queue depth.
- **Impact:** Latency in job execution completion.
- **Mitigation:** Worker daemon supports horizontal scaling across multiple pod replicas (`worker_pool.py`) with Redis consumer group load distribution (`XREADGROUP`, `XACK`). Kubernetes HPA triggers worker pod scale-out based on CPU/Queue metrics.
