# VertexERP AI — Production Deployment Guide
## Docker Compose, Kubernetes & Cloud Infrastructure Setup

**Version:** 2.0.0 Enterprise  
**Target Environments:** Production, Staging, Local Hybrid  

---

## 1. Architecture Infrastructure Stack

- **API & Application Server**: Python 3.11+ / FastAPI / Uvicorn (ASGI)
- **Frontend SPA**: React 18 / TypeScript / Vite / Tailwind CSS
- **Primary Relational Database**: PostgreSQL 16+ with `pgvector` extension
- **In-Memory Cache & Session Broker**: Redis 7+
- **Background Worker**: Celery / AsyncIO Background Ingestion Worker
- **Reverse Proxy & Ingress**: Nginx / Traefik with TLS 1.3 termination

---

## 2. Docker Compose Deployment (Recommended for Single-Node / On-Premise)

VertexERP AI includes production-ready Docker Compose configurations.

### A. Environment Configuration
Create `.env.production` at the project root:

```env
# Application Settings
ENVIRONMENT=production
DEBUG=false
APP_NAME="VertexERP AI Enterprise"
SECRET_KEY=generate_a_64_char_secure_random_hex_string_here
APP_URL=https://erp.yourdomain.com

# Database Connection
DATABASE_URL=postgresql+asyncpg://vertex_user:StrongDBPassword123!@postgres:5432/vertexerp_prod

# Redis Connection
REDIS_URL=redis://redis:6379/0

# Security & CORS
ALLOWED_ORIGINS=["https://erp.yourdomain.com"]
COOKIE_SECURE=true
COOKIE_DOMAIN=.yourdomain.com

# AI & OpenAI / Vertex Settings
OPENAI_API_KEY=your_openai_or_compatible_api_key
EMBEDDING_MODEL=text-embedding-3-small
```

### B. Launching the Services
```bash
# Build and launch all services in detached mode
docker compose -f docker-compose.prod.yml up -d --build

# Run database migrations
docker compose -f docker-compose.prod.yml exec api alembic upgrade head

# Seed initial enterprise demo tenant & roles (optional)
docker compose -f docker-compose.prod.yml exec api python -m scripts.seed_enterprise_demo
```

### C. Container Services Map
- `api`: FastAPI ASGI web service listening on port `8000`.
- `frontend`: High-performance Nginx web server serving compiled static assets on port `80` / `443`.
- `postgres`: PostgreSQL 16 with pgvector extension mounted to persistent volume `postgres_data`.
- `redis`: Redis server with persistent RDB snapshots mounted to volume `redis_data`.
- `worker`: Background task worker for RAG embedding generation and PDF document parsing.

---

## 3. Kubernetes Deployment

Production Kubernetes manifests are located in `deploy/k8s/`:

### A. Deploy Storage & Configs
```bash
kubectl apply -f deploy/k8s/namespace.yaml
kubectl apply -f deploy/k8s/secrets.yaml
kubectl apply -f deploy/k8s/configmap.yaml
```

### B. Deploy Core Workloads
```bash
kubectl apply -f deploy/k8s/postgres-statefulset.yaml
kubectl apply -f deploy/k8s/redis-deployment.yaml
kubectl apply -f deploy/k8s/api-deployment.yaml
kubectl apply -f deploy/k8s/frontend-deployment.yaml
kubectl apply -f deploy/k8s/ingress.yaml
```

### C. Scaling & High Availability
- Horizontal Pod Autoscaler (HPA) targets 70% CPU utilization across API pods.
- Readiness probes target `GET /api/v1/health/ready`.
- Liveness probes target `GET /api/v1/health/live`.

---

## 4. Production Maintenance & Health Checks

### Health Endpoints
- **Liveness Probe**: `GET /api/v1/health/live` (Checks process health).
- **Readiness Probe**: `GET /api/v1/health/ready` (Validates database and Redis connectivity).
- **Diagnostics**: `GET /api/v1/health/status` (Provides detailed latency metrics).
