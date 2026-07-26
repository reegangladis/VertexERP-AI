# Deployment Guide - VertexERP AI

This document provides deployment guidelines and Docker orchestration instructions for **VertexERP AI** Phase 1.

---

## 🐳 Docker Compose Deployment

The complete ERP ecosystem (database, cache, API server, and web client) is coordinated using `docker-compose.yml` located at the root of the workspace.

### 1. Build and Run Containers
To run the containers in detached mode:

```bash
docker compose up --build -d
```

### 2. Startup Sequencing
To prevent startup issues, the containers boot sequentially using depends_on conditions:
- **`postgres` & `redis`**: Boot first and run internal connection verification loops.
- **`backend`**: Starts only when database and cache pass healthcheck conditions.
- **`frontend`**: Starts only when backend healthcheck endpoint resolves successfully.

---

## 🩺 System Auditing & Monitoring

### Docker Health Checks
Verify service health using standard Docker commands:

```bash
docker compose ps
```

Healthchecks are run inside the containers:
- **Postgres**: Uses `pg_isready` check.
- **Redis**: Uses `redis-cli ping` check.
- **Backend API**: Uses `curl` mapping to `/api/v1/health`.
- **Frontend Nginx**: Uses `wget` spider request mapping to `/`.

### Operational Logs
Logs are mapped to local files inside `apps/api/logs/`:
- `app.log`: Application runtime traces.
- `error.log`: Fatal errors and exceptions.
- `access.log`: HTTP access logs and route response times.
