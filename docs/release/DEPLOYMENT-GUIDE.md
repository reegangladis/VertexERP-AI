# VertexERP AI V2 — Enterprise Production Deployment Guide

---

## 1. Prerequisites
- **Target OS**: Linux (Ubuntu 22.04 LTS / Debian 12 / RHEL 9) or Kubernetes >= 1.28
- **PostgreSQL**: PostgreSQL 16+ with `pgvector` extension installed
- **Redis**: Redis 7+ with Lua scripting enabled
- **Object Storage**: AWS S3 or MinIO
- **Docker & Compose**: Docker Engine >= 26.0, Docker Compose >= 2.25

---

## 2. Docker Compose Deployment (Staging / Production Single-Node)

### Step 1: Environment Configuration
Copy `.env.production.example` to `.env.production`:
```bash
cp .env.production.example .env.production
```
Configure required variables:
- `JWT_SECRET_KEY`: Minimum 32-character high-entropy secret
- `DATABASE_PASSWORD`: Strong PostgreSQL password
- `REDIS_PASSWORD`: Strong Redis authentication password
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY`: Enterprise AI credentials

### Step 2: Database Migration & Schema Upgrade
```bash
docker compose -f docker-compose.prod.yml run --rm migration
```

### Step 3: Launch Multi-Service Production Topology
```bash
docker compose -f docker-compose.prod.yml up -d
```

### Step 4: Verify Service Health
```bash
curl -f https://your-erp-domain.com/healthz
curl -f https://your-erp-domain.com/health/ready
```

---

## 3. Kubernetes Multi-Cluster Deployment

```bash
# 1. Apply Namespace & RBAC
kubectl apply -f infra/k8s/namespace.yaml

# 2. Apply ConfigMaps and Production Secrets
kubectl apply -f infra/k8s/configmap.yaml
kubectl apply -f infra/k8s/secret.prod.yaml

# 3. Execute Migration Job
kubectl apply -f infra/k8s/migration-job.yaml
kubectl wait --for=condition=complete --timeout=120s job/vertexerp-migration -n vertexerp-v2

# 4. Deploy API, Worker & Frontend Deployments
kubectl apply -f infra/k8s/api-deployment.yaml
kubectl apply -f infra/k8s/worker-deployment.yaml
kubectl apply -f infra/k8s/frontend-deployment.yaml
kubectl apply -f infra/k8s/ingress.yaml
```
