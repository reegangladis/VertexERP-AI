# Container Installation Guide - VertexERP AI

This guide contains instructions to deploy the complete multi-container architecture (PostgreSQL, Redis, FastAPI, Nginx-served React) with a single command using Docker Compose.

## Prerequisites
- Docker Engine installed (v20.10 or newer)
- Docker Compose installed (v2.0 or newer)

---

## 1. Single Command Deployment

From the root directory of the project, start the build sequence and launch the network services in background mode:

```bash
docker compose up --build -d
```

Compose coordinates the following initialization steps:
1. Builds postgres container, mounting the `postgres_data` volume and verifying readiness healthchecks.
2. Builds redis container, checking health states.
3. Builds `vertexerp_backend` using `docker/Dockerfile.api`, waiting until Postgres and Redis are fully online.
4. Builds `vertexerp_frontend` using `docker/Dockerfile.web`, mounting compiled React assets in Nginx and binding host port 3000.

---

## 2. Verify Deployments

Check running container states:
```bash
docker compose ps
```
All containers should report `Up (healthy)` or `Up`.

Test service endpoints:
- **Web UI Console**: `http://localhost:3000` (Browse the console overview, toggle themes, examine real-time API sync indicator)
- **FastAPI API Swagger Docs**: `http://localhost:8000/docs`
- **FastAPI Core Health Endpoint**:
  ```bash
  curl http://localhost:8000/api/v1/health
  ```
  Expected healthy response:
  ```json
  {"status":"healthy","version":"1.1.0","environment":"development","timestamp":"2026-07-23T...","services":{"database":"healthy","redis":"healthy"}}
  ```

---

## 3. Operations & Logs

Review system container logs:
```bash
# View backend logs in real-time
docker compose logs -f backend

# View database connections
docker compose logs postgres
```

Stop and clear containers (keeping data volumes intact):
```bash
docker compose down
```

Reset databases (warning: this destroys active local data storage):
```bash
docker compose down -v
```
