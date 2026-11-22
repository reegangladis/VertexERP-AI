# VertexERP AI V2 — Production Reality Audit

**Audit Date:** 2026-09-13  
**Auditing Standard:** Actual Source Code Truth Verification (Zero-Tolerance Reality Gate)  
**Previous Certification Status:** **REJECTED AND NULLIFIED**  
**Current Production Reality Status:** **NOT PRODUCTION READY (DEPLOYMENT FORBIDDEN)**  

---

## Evaluation Taxonomy

The following evaluation statuses are strictly applied based on verifiable source code evidence:
- **`IMPLEMENTED`**: Fully implemented in production-grade source code with actual execution paths and verified dependencies.
- **`PARTIAL`**: Partially implemented; key capabilities, security controls, or deployment configurations are missing.
- **`SIMULATED`**: The code contains stubbed, mocked, or in-memory representations returning fabricated success without performing actual operations.
- **`MISSING`**: Required production component, file, policy, or infrastructure manifest is completely absent.
- **`BROKEN`**: Implementation exists but contains functional defects, fatal logic errors, or invalid assumptions that fail in multi-replica production.
- **`NOT VERIFIED`**: Implementation cannot be verified due to lack of environment, tooling, or executable test coverage.

---

## 1. Multi-Tenancy & Row-Level Security (RLS)

**Status:** `CRITICAL — NOT IMPLEMENTED`

### Codebase Audit Findings
1. **Search for PostgreSQL RLS Directives:**
   - `CREATE POLICY`: **0 occurrences** across all 12 Alembic migration files and all SQL models.
   - `ENABLE ROW LEVEL SECURITY`: **0 occurrences** in migrations.
   - `FORCE ROW LEVEL SECURITY`: **0 occurrences** in migrations.
   - `current_setting('app.current_tenant_id')`: **0 occurrences** in PostgreSQL database migrations.
2. **Current Reality:**
   - In [`app/infrastructure/database/session.py`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/app/infrastructure/database/session.py#L82), the session executes `SET LOCAL app.current_tenant_id = :tenant_id`. However, because **no RLS policies exist in PostgreSQL**, this `SET LOCAL` is an empty no-op at the database engine level.
   - Multi-tenant data isolation is enforced **exclusively via application-level `WHERE tenant_id = :tenant_id` clauses** inside SQLAlchemy queries.
   - Any raw SQL query, developer omission of a WHERE filter, direct database connection, or compromised reporting query will leak data across all tenants without database-level protection.

### Tenant-Owned Table RLS Matrix
| Table Name | Application Filter | PostgreSQL RLS Enabled | PostgreSQL RLS Policy | RLS Status |
| :--- | :---: | :---: | :---: | :--- |
| `organizations` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `branches` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `departments` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `users` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `user_sessions` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `employees` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `crm_leads` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `crm_deals` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `inv_products` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `inv_stock_balances` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `inv_stock_movements`| Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `fin_accounts` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `fin_journals` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `fin_journal_lines` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `fin_invoices` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `fin_bills` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `mfg_production_orders`| Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `rag_documents` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `rag_document_chunks`| Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |
| `background_jobs` | Yes | No | None | `CRITICAL — NOT IMPLEMENTED` |

### Required Remediation Strategy
1. Create a dedicated Alembic migration (`0013_enforce_postgresql_rls.py`) iterating over all tenant-owned tables.
2. Execute for every tenant table:
   ```sql
   ALTER TABLE <table_name> ENABLE ROW LEVEL SECURITY;
   ALTER TABLE <table_name> FORCE ROW LEVEL SECURITY;
   CREATE POLICY <table_name>_tenant_isolation_policy ON <table_name>
       AS RESTRICTIVE
       USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
       WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);
   ```
3. Configure superuser bypass exceptions only for migration and maintenance database roles.

---

## 2. Database & Migrations

**Status:** `PARTIAL`

### Findings
- **Migration Chain:** 12 sequential Alembic migration files exist from `0001_v2_baseline_foundation` to `0012_background_processing_engine`. Chain is linear without branching.
- **ORM Model Consistency:** ORM models map to table definitions.
- **Deficiencies:**
  - PostgreSQL-specific features (`pgvector`, `RLS policies`) are absent from migrations.
  - Foreign key cascades are present on child tables (`ON DELETE CASCADE` on lines/items), but several parent-level relationships lack explicit restrict constraints on tenant references.
  - No automated migration downgrade tests are run against live PostgreSQL in CI.

---

## 3. RAG / Vector Search Architecture

**Status:** `SIMULATED (NOT PRODUCTION READY)`

### Codebase Audit Findings
1. **Database Schema ([`alembic/versions/0011_rag_knowledge_domain.py`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/alembic/versions/0011_rag_knowledge_domain.py#L90)):**
   - Chunks store embeddings in a generic JSON column:
     ```python
     sa.Column("embedding_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True)
     ```
   - **No `vector` column** is created.
   - **No HNSW or IVFFlat index** is defined in PostgreSQL.
   - `CREATE EXTENSION IF NOT EXISTS vector` is never executed in migrations.
2. **Search Implementation ([`app/modules/ai/rag/retriever.py`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/app/modules/ai/rag/retriever.py#L138-L203)):**
   - The retriever executes a SQL query fetching **all chunks for the tenant**:
     ```python
     stmt = select(RAGDocumentChunk, RAGDocument, RAGDocumentVersion)...
     rows = (await session.execute(stmt)).all()
     ```
   - It iterates through every row in Python, deserializes JSON, and calculates `self._cosine_similarity(query_vector, embedding)` in memory.
   - It sorts the entire in-memory list with `candidates.sort(key=lambda x: x.vector_score, reverse=True)` and slices `[:top_k]`.

### Production Impact
- **Severe Scalability Failure:** With 100,000 document chunks, every user prompt causes a full table scan, transferring megabytes of JSON across the wire and performing hundreds of thousands of Python floating-point calculations, consuming excessive CPU and locking worker threads.

### Required Remediation
1. Add `CREATE EXTENSION IF NOT EXISTS vector;` in an Alembic migration.
2. Alter `rag_document_chunks` to replace `embedding_json` with `embedding vector(1536)` (or 3072 depending on model dimension).
3. Add HNSW cosine index:
   ```sql
   CREATE INDEX idx_rag_chunks_vector_hnsw ON rag_document_chunks 
   USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
   ```
4. Update `RAGRetriever` to execute native vector distance queries:
   ```python
   stmt = select(RAGDocumentChunk).order_by(RAGDocumentChunk.embedding.cosine_distance(query_vector)).limit(top_k)
   ```

---

## 4. Frontend Authentication

**Status:** `CRITICAL — BROKEN / SIMULATED`

### Codebase Audit Findings
1. **Hardcoded User Session ([`frontend/src/stores/auth-store.ts`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/frontend/src/stores/auth-store.ts#L26-L60)):**
   ```typescript
   export const useAuthStore = create<UserSessionState>((set, get) => ({
     userId: "user-admin-001",
     email: "admin@vertexerp.io",
     fullName: "Principal Administrator",
     tenantId: "tenant-root-001",
     organizationId: "org-primary-001",
     roles: ["TenantAdmin"],
     permissions: [ ... ],
     isAuthenticated: true,  // <-- HARDCODED TRUE ON STARTUP
   ```
2. **Current Reality:**
   - The frontend application starts with `isAuthenticated: true` by default.
   - No unauthenticated redirect occurs; any user opening the browser is treated as a fully authenticated `TenantAdmin`.
   - When API calls fail with HTTP 401 (because backend tokens are absent or expired), the UI remains on authenticated dashboard pages in broken states instead of redirecting to `/login`.
   - No `/api/v1/auth/me` session bootstrap query is executed on mount.

### Required Remediation
1. Reset initial Zustand store state to `isAuthenticated: false`, `userId: null`, `email: null`, `roles: []`, `permissions: []`.
2. Implement an `AuthBootstrap` component that calls `/api/v1/auth/me` with loading skeleton.
3. Add router navigation guards redirecting unauthenticated users to `/login`.

---

## 5. Token Storage

**Status:** `BROKEN / INSECURE`

### Codebase Audit Findings
1. **LocalStorage Usage ([`frontend/src/stores/auth-store.ts`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/frontend/src/stores/auth-store.ts#L63)):**
   ```typescript
   localStorage.setItem("access_token", payload.token);
   ```
2. **API Client Header Injection ([`frontend/src/lib/api-client.ts`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/frontend/src/lib/api-client.ts#L34)):**
   ```typescript
   const token = localStorage.getItem("access_token");
   if (token) headers.set("Authorization", `Bearer ${token}`);
   ```
3. **Current Reality:**
   - Tokens stored in `localStorage` are vulnerable to Cross-Site Scripting (XSS) exfiltration.
   - Browser authentication does not use `Secure`, `HttpOnly`, `SameSite=Lax` cookies.

### Required Remediation
1. Update backend `/api/v1/auth/login` and `/api/v1/auth/refresh` endpoints to set `access_token` and `refresh_token` as `HttpOnly`, `Secure`, `SameSite=Lax` cookies.
2. Remove `localStorage` access token reads and writes from the frontend.
3. Configure `fetch` / `apiClient` with `credentials: "include"`.

---

## 6. JWT Security

**Status:** `PARTIAL`

### Findings
- **Algorithm:** Uses symmetric `HS256` HMAC-SHA256 with `JWT_SECRET_KEY` ([`app/core/security.py`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/app/core/security.py#L165)).
- **Asymmetric Signing:** Documentation claims "RS256/asymmetric", but **no asymmetric key pairs (RSA/ECDSA/Ed25519)**, `kid` key management, or JWKS endpoints exist.
- **Security Assessment:** HS256 is functional for single-service deployments if the secret is strong (32+ chars), but documentation claiming RS256 is false.

---

## 7. Background Jobs Engine

**Status:** `CRITICAL — SIMULATED / NOT PRODUCTION READY`

### Codebase Audit Findings
1. **In-Memory Queue ([`app/modules/jobs/engine/job_queue.py`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/app/modules/jobs/engine/job_queue.py#L19-L23)):**
   ```python
   self._queues: dict[int, asyncio.Queue] = {
       JobPriority.CRITICAL.value: asyncio.Queue(),
       JobPriority.HIGH.value: asyncio.Queue(),
       JobPriority.NORMAL.value: asyncio.Queue(),
   }
   self._delayed_heap: list[tuple[float, int, str]] = []
   ```
2. **Current Reality:**
   - The queue is **strictly in-memory (`asyncio.Queue`) within a single Python process**.
   - **Pod Restarts Destroy Jobs:** If the API pod or worker restarts, all in-memory queued and delayed jobs are immediately lost.
   - **No Multi-Replica Support:** Running 3 replicas of the API container results in 3 disconnected in-memory queues; background worker pods cannot dequeue jobs submitted to API pods.
   - **No Lease / Visibility Handling:** No distributed lock or atomic lease acknowledgment exists.

### Required Remediation
- Implement a durable distributed queue using **Celery + Redis** or **Redis Streams + Lua atomic claiming**:
  - `XADD` for durable enqueue into Redis.
  - `XREADGROUP` / consumer groups for worker claiming and lease visibility timeouts.
  - `XACK` on job completion; PEL (Pending Entries List) sweeper for dead worker recovery.

---

## 8. Scheduler

**Status:** `BROKEN / NOT EXECUTING`

### Codebase Audit Findings
1. **Scheduler Definition ([`app/modules/jobs/engine/scheduler.py`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/app/modules/jobs/engine/scheduler.py#L46)):**
   - `CronScheduler.evaluate_schedules()` is implemented as a class method.
2. **Execution Reality:**
   - **`CronScheduler.evaluate_schedules` is NEVER called by any running loop or background daemon in `app/worker.py`, `app/main.py`, or anywhere in the runtime.**
   - The only place `evaluate_schedules` was ever executed is in `tests/jobs/test_background_processing.py`.
   - In a running deployment, recurring cron schedules **never trigger automatically**.

### Required Remediation
1. Integrate a dedicated scheduler loop (e.g. Celery Beat or a continuous `asyncio.create_task` ticker with distributed Redis locking) in `app/worker.py` running every 60 seconds.

---

## 9. Workers Reality

**Status:** `SIMULATED`

| Worker | Implementation File | Actual Implementation Status | Reality Detail |
| :--- | :--- | :---: | :--- |
| **EmailWorker** | [`email_worker.py`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/app/modules/jobs/workers/email_worker.py) | `SIMULATED` | Formats string template and returns `"status": "DELIVERED"`. **No SMTP / SendGrid / SES client is called.** |
| **NotificationsWorker** | [`notifications_worker.py`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/app/modules/jobs/workers/notifications_worker.py) | `SIMULATED` | Logs message and returns `"status": "DELIVERED"`. **No websocket, push, or Slack API is called.** |
| **ReportsWorker** | [`reports_worker.py`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/app/modules/jobs/workers/reports_worker.py) | `IMPLEMENTED` | Queries real database models (`JournalLine`, `StockBalance`) and formats CSV/JSON output. |
| **ScheduledJobsWorker** | [`scheduled_jobs_worker.py`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/app/modules/jobs/workers/scheduled_jobs_worker.py#L40-L65) | `SIMULATED` | **Returns hardcoded mock dictionary:** `{"warehouses_scanned": 4, "skus_evaluated": 128, ...}` without executing real queries. |
| **IntegrationsWorker** | [`integrations_worker.py`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/app/modules/jobs/workers/integrations_worker.py#L82) | `SIMULATED` | Computes HMAC signature with hardcoded default key, then returns `{"success": True}` **without sending an HTTP request**. |
| **DocumentIngestionWorker** | [`document_ingestion_worker.py`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/app/modules/jobs/workers/document_ingestion_worker.py) | `IMPLEMENTED` | Parses markdown/text, generates chunks, and inserts them into the database. |
| **EmbeddingsWorker** | [`embeddings_worker.py`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/app/modules/jobs/workers/embeddings_worker.py) | `PARTIAL` | Calls embedding service, but embeddings are stored in `JSONB` instead of vector column. |

---

## 10. Integrations & Outbound HTTP

**Status:** `SIMULATED / INSECURE`

### Findings
- **No Outbound HTTP Dispatch:** `IntegrationsWorker` validates URLs against SSRF and computes HMAC-SHA256, but lacks `httpx.AsyncClient` dispatch.
- **Hardcoded Secrets:** Uses fallback hardcoded secret `"vertexerp_secret_key_v2"` on line 39 of `integrations_worker.py`.

---

## 11. Object Storage

**Status:** `MISSING`

### Findings
- In `app/infrastructure/`, only `database` and `redis` exist.
- **No S3 / MinIO storage adapter, upload client, or presigned URL generator exists** in the application codebase.
- File uploads directly serialize text into database columns or local files.

---

## 12. Frontend API Integration

**Status:** `PARTIAL`

### Findings
- Most domain feature modules (`organization`, `hr`, `crm`, `finance`, `manufacturing`, `analytics`) implement TanStack React Query hooks mapping to `/api/v1/...` endpoints.
- However, because the auth store is hardcoded to `isAuthenticated: true` without real login redirect guards, unauthenticated or expired states fail with silent query errors.

---

## 13. Testing & Test Environment Reproducibility

**Status:** `CRITICAL — BROKEN`

### Codebase Audit Findings
1. **SQLite In-Memory Mock Testing ([`tests/conftest.py`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/tests/conftest.py#L54)):**
   - All 189 backend pytest tests run against `sqlite+aiosqlite:///:memory:` with mock compilation hooks for `JSONB`, `UUID`, and `INET`.
   - **Zero tests run against real PostgreSQL during standard `pytest tests/`.**
   - PostgreSQL-specific features (`pgvector`, `RLS`, `SET LOCAL`, `now()`, `clock_timestamp()`, PostgreSQL JSONB operators) are never exercised or validated by the test runner.
2. **Undeclared Test Dependencies ([`pyproject.toml`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/pyproject.toml)):**
   - `aiosqlite` and `fakeredis` are used in `conftest.py` but **omitted from `pyproject.toml` dependencies**.

---

## 14. CI/CD Workflows

**Status:** `MISSING`

### Findings
- `.github/workflows/` is **completely absent**.
- No automated CI pipelines exist for backend tests, frontend tests, linting, Docker builds, or security scanning on pull requests.

---

## 15. Docker & Containerization

**Status:** `IMPLEMENTED`

### Findings
- Multi-stage Dockerfiles exist for backend (`Dockerfile`) and frontend (`frontend/Dockerfile`).
- Non-root user execution (`UID 10001` backend, `UID 101` frontend) and `tini` PID 1 init process are verified.
- `docker-compose.yml`, `docker-compose.staging.yml`, and `docker-compose.prod.yml` exist.

---

## 16. Nginx & TLS Configuration

**Status:** `PARTIAL / BROKEN`

### Findings
- In [`infra/nginx/conf.d/vertexerp.conf`](file:///c:/Users/ExcelR/Music/VertexERP-AI/reference project/infra/nginx/conf.d/vertexerp.conf#L21), only `listen 80;` is configured.
- **Port 443 SSL listener, `ssl_certificate` directives, and HTTP -> HTTPS redirect (`return 301 https://$host$request_uri;`) are MISSING.**

---

## 17. Kubernetes Manifests

**Status:** `PARTIAL`

### Findings
- Manifests exist in `infra/k8s/` for Deployments, Services, Ingress, ConfigMap, and Migration Job.
- **Topology Ambiguity:** `configmap.yaml` references `vertexerp-postgres-service` and `vertexerp-redis-service`, but **no StatefulSet or ExternalName manifests exist** to define whether DB/Redis are in-cluster or managed cloud services.

---

## 18. Backup & Disaster Recovery

**Status:** `PARTIAL`

### Findings
- Cold backup generation and AES-256-GCM encryption scripts exist (`scripts/backup_database.py`, `scripts/restore_database.py`).
- **Continuous WAL streaming / PITR is SIMULATED in documentation only** (no PostgreSQL `archive_command` or pgBackRest configured).

---

## 19. Security Review Summary

| Security Domain | Status | Reality Assessment |
| :--- | :---: | :--- |
| **PostgreSQL RLS** | `CRITICAL — NOT IMPLEMENTED` | No RLS policies in database; isolation depends solely on app code. |
| **Frontend Auth State** | `CRITICAL — BROKEN` | Default `isAuthenticated: true` as `TenantAdmin` in browser bundle. |
| **Token Storage (XSS)** | `BROKEN` | Access tokens stored in `localStorage` instead of HttpOnly cookies. |
| **Queue Durability** | `CRITICAL — SIMULATED` | In-memory `asyncio.Queue`; jobs lost on pod restart. |
| **RAG Vector Isolation** | `SIMULATED` | In-memory Python cosine similarity over JSONB column; no pgvector HNSW index. |
| **Worker Operations** | `SIMULATED` | Email, notifications, and scheduled jobs fabricate success without network ops. |
| **TLS Enforcement** | `BROKEN` | Nginx reverse proxy listens only on HTTP port 80. |
| **CI/CD Automation** | `MISSING` | No automated GitHub Actions workflows. |
