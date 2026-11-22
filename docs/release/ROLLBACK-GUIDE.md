# VertexERP AI V2 — Production Rollback & Recovery Guide

---

## 1. Application Deployment Rollback

### Docker Compose
To revert to a previous container release image:
```bash
# 1. Update image tags in .env.production
IMAGE_TAG=v2.0.0-previous

# 2. Recreate containers
docker compose -f docker-compose.prod.yml up -d --force-recreate
```

### Kubernetes
```bash
# Rollback API Deployment
kubectl rollout undo deployment/vertexerp-api -n vertexerp-v2

# Rollback Worker Daemon
kubectl rollout undo deployment/vertexerp-worker -n vertexerp-v2

# Rollback Frontend SPA
kubectl rollout undo deployment/vertexerp-frontend -n vertexerp-v2

# Verify Rollback Status
kubectl rollout status deployment/vertexerp-api -n vertexerp-v2
```

---

## 2. Database Schema Rollback

If a migration must be reverted:
```bash
# Revert single migration step
alembic downgrade -1

# Revert to specific revision ID
alembic downgrade 0012_analytics_reporting_kpi
```
> [!IMPORTANT]
> Always create a pre-migration database snapshot before applying major schema revisions.
