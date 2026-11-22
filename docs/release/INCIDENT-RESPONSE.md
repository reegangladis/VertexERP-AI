# VertexERP AI V2 — Incident Response & Triage Runbook

---

## 1. Severity Levels & SLA Response Times

| Severity | Definition | Target Initial Response | Target Resolution |
| :--- | :--- | :---: | :---: |
| **SEV-1 (Critical)** | Core ERP API down, database inaccessible, data integrity compromised. | < 15 minutes | < 2 hours |
| **SEV-2 (High)** | Degradation in background worker processing, AI Copilot offline. | < 30 minutes | < 6 hours |
| **SEV-3 (Medium)** | Minor non-blocking UI issue or transient timeout on bulk reporting. | < 2 hours | < 24 hours |
| **SEV-4 (Low)** | Informational or cosmetic defect. | < 1 business day | Next sprint |

---

## 2. Triage & Diagnostic Commands

### Check Pod & Container Health
```bash
# Kubernetes
kubectl get pods -n vertexerp-v2
kubectl logs -l app.kubernetes.io/name=vertexerp-api -n vertexerp-v2 --tail=100
kubectl logs -l app.kubernetes.io/name=vertexerp-worker -n vertexerp-v2 --tail=100

# Docker Compose
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=100 api
docker compose -f docker-compose.prod.yml logs --tail=100 worker
```

### Check Database Connection Pool & Locks
```sql
SELECT count(*), state FROM pg_stat_activity GROUP BY state;
SELECT pid, query, age(clock_timestamp(), query_start) FROM pg_stat_activity WHERE state != 'idle' ORDER BY age DESC LIMIT 10;
```

### Check Redis Stream Consumer Lag
```bash
redis-cli XINFO GROUPS vertexerp:jobs:stream
redis-cli XLEN vertexerp:jobs:stream
```
