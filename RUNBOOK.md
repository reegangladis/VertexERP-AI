# VertexERP AI V2 — Runbook

## 1. Recommended development startup (Docker Desktop)

Requirements:
- Docker Desktop with Compose
- Node.js 20+ only if running the frontend outside Docker
- Git

From the project root:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

The development stack provides:
- PostgreSQL 16 + pgvector
- Redis 7
- MinIO
- Alembic migrations
- FastAPI API
- Background worker + scheduler
- Vite frontend

Open:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- MinIO console: http://localhost:9001

The migration service runs before the API/worker.

## 2. Run backend directly on Windows

Use Python 3.12 (the project tooling target):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Start PostgreSQL/Redis/MinIO first, then:

```powershell
alembic upgrade head
python -m uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```powershell
.\.venv\Scripts\Activate.ps1
python -m app.worker
```

## 3. Run frontend directly

```powershell
cd frontend
npm ci
npm run dev
```

The Vite development proxy forwards `/api` to `http://127.0.0.1:8000`.

## 4. Verification

Backend:

```powershell
python -m compileall app tests scripts
python -m pytest tests -v
```

Frontend:

```powershell
cd frontend
npm run lint
npm run test
npm run build
```

Infrastructure:

```powershell
docker compose config
docker compose -f docker-compose.prod.yml config
docker compose -f docker-compose.staging.yml config
```

Database:

```powershell
alembic upgrade head
alembic current
```

## 5. Important production settings

Do not use `.env.example` values in production.

Copy `.env.production.example` to `.env.production` and replace every `REPLACE_WITH_*` value with real secrets.

For browser authentication:
- production/staging use Secure HttpOnly cookies
- development uses HttpOnly cookies without the Secure flag so localhost HTTP works

For S3-compatible storage:
- `STORAGE_ENDPOINT_URL` must be reachable by the API
- `STORAGE_PUBLIC_ENDPOINT_URL` is used for object URLs
- presigned browser downloads require the configured S3 endpoint to be reachable by the browser

## 6. Architecture safeguards included in this release

- PostgreSQL RLS migration dynamically protects every public table that has a `tenant_id` column.
- Tenant bootstrap establishes the PostgreSQL tenant context before creating tenant-owned records.
- Login/refresh use a tightly scoped authentication bootstrap path before tenant context is known.
- pgvector native `vector(1536)` storage and HNSW indexing are enabled by migration 0014.
- RAG indexing writes native vectors.
- PostgreSQL RAG retrieval uses pgvector cosine distance; SQLite remains only a unit-test fallback.
- Redis Streams use consumer groups and stale-message reclamation.
- Stream messages are acknowledged after job execution rather than before it.
- Scheduled jobs are placed onto the queue after their database transaction commits.
- Object storage uses real S3/MinIO operations rather than returning simulated bytes.
- Development Compose runs migrations before API/worker startup.
- Production MinIO is reachable from the reverse-proxy network.
- Release CI references the actual root Dockerfile.
- Security CI no longer masks dependency-audit failures.

## 7. Reference project

`reference project` is not part of this release and must remain read-only.
