# VertexERP AI V2 — Production Environment Specification

---

## 1. System Topology Architecture

```
Internet / Clients
       │
       ▼ (Port 443 HTTPS / TLS 1.3)
┌──────────────────────────────────────────────┐
│  Nginx Reverse Proxy & Load Balancer         │
│  - Port 443 SSL Termination                  │
│  - Port 80 HTTP -> 301 HTTPS Redirection     │
│  - HSTS, CSP, X-Frame-Options Hardened       │
└───────┬──────────────────────┬───────────────┘
        │                      │
        ▼                      ▼
┌──────────────────┐   ┌───────────────────────────┐
│ Frontend Webapp  │   │ Backend FastAPI Service   │
│ Nginx SPA (80)   │   │ ASGI Cluster (Port 8000)  │
└──────────────────┘   └───────────┬───────────────┘
                                   │
              ┌────────────────────┼───────────────────┐
              │                    │                   │
              ▼                    ▼                   ▼
    ┌──────────────────┐  ┌──────────────────┐ ┌──────────────┐
    │  PostgreSQL 16   │  │  Redis 7 Cluster │ │ MinIO / S3   │
    │  + pgvector      │  │  Streams & Lock  │ │ Tenant Bucket│
    │  + Row-Level Sec │  │  Broker (6379)   │ │ (Port 9000)  │
    └──────────────────┘  └────────┬─────────┘ └──────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ Worker Daemon        │
                        │ - Redis Streams Con. │
                        │ - Cron Scheduler     │
                        └──────────────────────┘
```

---

## 2. Infrastructure Sizing Matrix

| Component | Minimum (Staging) | Production Recommended | Multi-Node Enterprise |
| :--- | :--- | :--- | :--- |
| **API Replicas** | 2 pods (1 CPU, 2GB RAM) | 4 pods (2 CPU, 4GB RAM) | 8+ pods with HPA (up to 20) |
| **Worker Replicas**| 1 pod (1 CPU, 2GB RAM) | 2 pods (2 CPU, 4GB RAM) | 4+ pods with HPA |
| **PostgreSQL** | 2 CPU, 4GB RAM, 50GB SSD | 4 CPU, 16GB RAM, 200GB NVMe | Managed RDS Aurora (8 vCPU, 32GB) |
| **Redis** | 1 CPU, 2GB RAM | 2 CPU, 4GB RAM | Managed Redis / ElastiCache Multi-AZ |
| **Frontend** | 2 pods (0.5 CPU, 512MB) | 3 pods (1 CPU, 1GB RAM) | 5+ pods |
