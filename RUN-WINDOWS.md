# VertexERP AI V2 — Windows Run & Deployment Guide

This package is a production-oriented VertexERP AI V2 release candidate with a reproducible local Docker environment and production deployment manifests.

## 1. Fastest way to see the application

Requirements:

- Windows 10/11
- Docker Desktop with Linux containers
- PowerShell
- At least 8 GB RAM recommended for the full stack

Open PowerShell in this project directory and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\run-local.ps1
```

The launcher:

1. verifies Docker;
2. builds the backend and frontend;
3. starts PostgreSQL + pgvector;
4. starts Redis;
5. starts MinIO;
6. runs Alembic migrations;
7. starts the FastAPI API;
8. starts the background worker;
9. starts the React/Vite frontend;
10. creates the development demo tenant/user if it does not exist;
11. opens the login page.

### Demo login

- Email: `testuser@example.com`
- Password: `Test@12345678`
- Tenant: `test-company`

This account is for local development/demo use only. Do not use this credential in staging or production.

## 2. Verify the running system

Run:

```powershell
.\scripts\verify-local.ps1
```

The verification checks:

- API liveness
- API readiness
- OpenAPI
- frontend availability
- login HTTP 200
- HttpOnly access cookie creation
- access cookie size below the 4096-byte browser limit
- `/me` authentication
- server-side effective RBAC permissions

No access/refresh token values are printed.

## 3. Useful URLs

- Frontend: http://localhost:3000/login
- API Swagger: http://localhost:8000/docs
- API OpenAPI: http://localhost:8000/openapi.json
- MinIO console: http://localhost:9001

## 4. Stop the local stack

```powershell
.\scripts\stop-local.ps1
```

This stops containers but preserves Docker volumes.

To intentionally delete local development data:

```powershell
docker compose down -v
```

That command deletes the local PostgreSQL/Redis/MinIO volumes.

## 5. What the local stack verifies

The local environment contains:

```text
Browser
  |
  v
React/Vite frontend :3000
  |
  | /api proxy
  v
FastAPI :8000
  |
  +--> PostgreSQL 16 + pgvector :5432
  +--> Redis 7.2 :6379
  +--> MinIO :9000/:9001
  |
  +--> background worker
```

Authentication uses HttpOnly cookies. The access JWT intentionally does not carry the full granular permission list. Permissions are resolved server-side through RBAC with tenant-scoped Redis caching.

## 6. Staging deployment

Do not use production credentials in source control.

Create a staging environment file from:

```text
.env.staging.example
```

Populate at minimum:

- JWT_SECRET_KEY
- INTEGRATION_SIGNING_SECRET
- DATABASE_PASSWORD
- STORAGE_SECRET_KEY
- STORAGE_ACCESS_KEY
- AI provider API key if a real AI provider is selected
- ALLOWED_ORIGINS
- ALLOWED_HOSTS

Then validate:

```powershell
docker compose -f docker-compose.staging.yml config
```

A missing required staging secret must cause Compose/configuration to fail rather than silently using a fallback password.

## 7. Production deployment

Production requires real infrastructure and real secrets. The repository cannot safely embed those values.

Recommended architecture:

- managed PostgreSQL 16 with pgvector
- managed Redis
- S3-compatible object storage with versioning/Object Lock where required
- Kubernetes or a hardened container platform
- TLS certificate managed by a trusted CA/cert-manager
- external secret manager
- centralized logs/metrics
- tested backup and restore

The included `docker-compose.prod.yml` is useful for controlled single-host production deployments, but it still requires:

1. `.env.production`
2. real TLS certificates mounted at `infra/nginx/ssl/live/fullchain.pem` and `privkey.pem`
3. real domain/DNS
4. real PostgreSQL/Redis/S3 credentials
5. a real AI provider key if AI is enabled
6. tested backup/restore
7. host firewall and OS hardening

For Kubernetes, review all manifests under `infra/k8s/`. The application tier is hardened with non-root containers, read-only filesystems where supported, dropped Linux capabilities, service accounts without token automount, probes, HPA/PDB configuration, and NetworkPolicies.

The Kubernetes configuration expects PostgreSQL/Redis endpoints named by the production ConfigMap. If you use managed services, update those endpoints and the corresponding network controls for your cloud network.

## 8. Production readiness rule

A green local run does not by itself prove production readiness.

Before a real production launch, verify:

- all automated tests pass in CI;
- Docker images build from a clean checkout;
- migrations run successfully against a production-like PostgreSQL;
- RLS tenant isolation is tested against two tenants;
- RBAC changes take effect without issuing a new JWT;
- access cookies remain below browser limits;
- refresh rotation and replay detection work;
- logout/session revocation work;
- AI provider credentials are stored outside source control;
- RAG documents and vectors remain tenant-isolated;
- backups have been restored successfully;
- monitoring and alerting are active;
- TLS and DNS are verified externally;
- load/resource limits are appropriate for the target infrastructure.

## 9. CI/CD

The release workflow builds:

- backend image from `Dockerfile`
- worker image from `Dockerfile`
- frontend image from `frontend/Dockerfile`

The security workflow is configured to fail on high-severity dependency audit findings rather than masking failures.

## 10. Security note

Do not commit:

- `.env`
- production secrets
- real API keys
- private TLS keys
- Kubernetes Secret values

Use a secrets manager or CI/CD secret store.

