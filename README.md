# VertexERP AI V2 — Production Multi-Tenant Enterprise Platform

VertexERP AI V2 is an enterprise-grade, cloud-native ERP platform featuring native AI Copilot & RAG, comprehensive business domain modules (HR, CRM, Inventory, Procurement, Finance, Manufacturing, Analytics), strict multi-tenancy with PostgreSQL Row-Level Security (RLS), durable background job processing via Redis Streams, and a modern React 19 / Vite frontend.

---

## 🏗️ Architecture & Technology Stack

- **Backend Framework:** FastAPI 0.115+ (Python 3.12+) with Async I/O
- **Frontend Application:** React 19 + TypeScript + Vite + Tailwind CSS + Zustand + React Query
- **Database Engine:** PostgreSQL 16 Enterprise with `pgvector` HNSW indexes
- **Multi-Tenancy:** PostgreSQL Row-Level Security (RLS) + Tenant-Scoped Sessions
- **Distributed Broker & Cache:** Redis 7 (Redis Streams, Consumer Groups, Distributed Locks)
- **Object Storage:** S3 / MinIO Tenant-Scoped Storage Client
- **Database Migrations:** Alembic with strictly ordered, non-branching migrations
- **Observability:** Structured JSON logging, Prometheus metrics registry, PII masking, RFC 7807 error responses
- **Security:** Argon2id password hashing, HttpOnly Secure cookies, JWT token rotation, Zero-trust SSRF filtering
- **Infrastructure:** Multi-stage Dockerfiles, Docker Compose, Kubernetes 1.28+ manifests, Nginx TLS termination

---

## 🚀 Quickstart & Local Setup

### 1. Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1 | Linux/macOS: source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Launch local dependencies (PostgreSQL 16 + Redis 7 + MinIO)
docker compose up -d

# Execute database migrations
alembic upgrade head

# Run FastAPI backend API server
python -m uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload

# Run background worker daemon
python -m app.worker
```

### 2. Frontend Setup
```bash
cd frontend
npm ci
npm run dev
```

---

## 🧪 Comprehensive Verification Commands

```bash
# Python Linting & Formatting
ruff check app/ tests/ scripts/
ruff format --check app/ tests/ scripts/

# Static Type Checking
mypy app/

# Full Backend Test Suite
pytest tests/ -v

# Frontend TypeScript & Vitest Tests
npm --prefix frontend run lint
npm --prefix frontend run test
npm --prefix frontend run build

# Infrastructure & Manifest Validation
python scripts/validate_infra.py
```

---

## 🚢 Staging & Production Deployment

### Docker Compose
```bash
# Configure production secrets in .env.production
cp .env.production.example .env.production

# Run migrations and start production services
docker compose -f docker-compose.prod.yml run --rm migration
docker compose -f docker-compose.prod.yml up -d
```

### Kubernetes
```bash
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/configmap.yaml
kubectl apply -f infra/k8s/secret.template.yaml
kubectl apply -f infra/k8s/migration-job.yaml
kubectl apply -f infra/k8s/api-deployment.yaml
kubectl apply -f infra/k8s/worker-deployment.yaml
kubectl apply -f infra/k8s/frontend-deployment.yaml
kubectl apply -f infra/k8s/ingress.yaml
```

---

## 📚 Production Documentation Catalog

- **Final Readiness Gate:** [`docs/release/FINAL-PRODUCTION-READINESS.md`](docs/release/FINAL-PRODUCTION-READINESS.md)
- **Verification Evidence:** [`docs/release/FINAL-VERIFICATION-EVIDENCE.md`](docs/release/FINAL-VERIFICATION-EVIDENCE.md)
- **Deployment Guide:** [`docs/release/DEPLOYMENT-GUIDE.md`](docs/release/DEPLOYMENT-GUIDE.md)
- **Rollback Guide:** [`docs/release/ROLLBACK-GUIDE.md`](docs/release/ROLLBACK-GUIDE.md)
- **Database Migration Guide:** [`docs/release/DATABASE-MIGRATION-GUIDE.md`](docs/release/DATABASE-MIGRATION-GUIDE.md)
- **Backup & Restore Guide:** [`docs/release/BACKUP-RESTORE-GUIDE.md`](docs/release/BACKUP-RESTORE-GUIDE.md)
- **Incident Response Runbook:** [`docs/release/INCIDENT-RESPONSE.md`](docs/release/INCIDENT-RESPONSE.md)
- **Production Environment Spec:** [`docs/release/PRODUCTION-ENVIRONMENT.md`](docs/release/PRODUCTION-ENVIRONMENT.md)
- **Known Limitations:** [`docs/release/KNOWN-LIMITATIONS.md`](docs/release/KNOWN-LIMITATIONS.md)
- **Remaining Operational Risks:** [`docs/release/REMAINING-RISKS.md`](docs/release/REMAINING-RISKS.md)
