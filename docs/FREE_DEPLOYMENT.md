# VertexERP AI V2 - $0/Month Free Cloud Deployment Guide

This guide provides step-by-step instructions to deploy **VertexERP AI V2** completely free of charge ($0/month) using free-tier cloud providers, while preserving all enterprise-grade security controls, PostgreSQL Row-Level Security (RLS), multi-tenant isolation, and background job processing.

---

## 1. Architecture Overview: Free / Demo Mode vs Production Mode

```
                                GitHub Repository
                               (main / release)
                                      │
                   ┌──────────────────┴──────────────────┐
                   │                                     │
                   ▼                                     ▼
             Vercel Hobby                           Render Free
          React 19 Frontend                     FastAPI ASGI Web API
       (Custom Domain / SSL)                  (Auto-Sleep on Inactivity)
                   │                                     │
                   │ (HTTPS / CORS REST API)             │
                   └─────────────────────────────────────┤
                                                         │
                                        ┌────────────────┴────────────────┐
                                        │                                 │
                                        ▼                                 ▼
                                  Supabase Free                     Upstash Redis
                             PostgreSQL 16 + pgvector             Serverless Redis
                              (RLS Multi-Tenancy)               (Rate Limit & Revocation)
                                        │
                                        ▼
                             Cloudflare R2 / S3
                           (Optional Free Storage)
```

### Architectural Comparison

| Component | Production Mode (`render.yaml`) | Free / Demo Mode (`render.free.yaml`) | Free Tier Quota / Limits |
| :--- | :--- | :--- | :--- |
| **Frontend** | Vercel Pro / Nginx Cluster | **Vercel Hobby** | Unlimited deployments, 100 GB bandwidth/mo |
| **API Backend** | Render Standard Web Service ($25+/mo) | **Render Free Web Service** | 512 MB RAM, 0.1 CPU, spins down after 15m idle |
| **Database** | Render Managed PostgreSQL ($20+/mo) | **Supabase Free PostgreSQL 16** | 500 MB DB storage, native `pgvector`, pooling |
| **Cache & Queue** | Render Managed Redis ($10+/mo) | **Upstash Redis Free** | 10,000 commands/day, 256 MB data, TLS `rediss://` |
| **Background Worker** | Render Background Worker Daemon ($25+/mo) | **Embedded ASGI Worker Pool** | Runs asynchronously within FastAPI event loop |
| **Object Storage** | AWS S3 / Dedicated MinIO | **Cloudflare R2 / Supabase Storage** | 10 GB free storage, $0 egress fees |
| **Monthly Cost** | **~$80 - $150 / month** | **$0.00 / month** | 100% Free Forever Tiers |

---

## 2. Required Free-Tier Accounts

Before beginning deployment, create accounts on the following platforms (all have free tiers without upfront credit card requirements or $0 charges):

1. **GitHub**: [github.com](https://github.com) (Holds your repository)
2. **Supabase**: [supabase.com](https://supabase.com) (Free PostgreSQL 16 + pgvector)
3. **Upstash**: [upstash.com](https://upstash.com) (Free serverless Redis)
4. **Render**: [render.com](https://render.com) (Free Web Service for FastAPI)
5. **Vercel**: [vercel.com](https://vercel.com) (Free Hobby hosting for React frontend)
6. *(Optional)* **Cloudflare**: [cloudflare.com](https://cloudflare.com) (R2 Object Storage)

---

## 3. Step-by-Step Setup

### Step 1: Provision Supabase PostgreSQL Database

1. Log in to [Supabase](https://supabase.com/dashboard) and click **New Project**.
2. Set a **Project Name** (e.g., `vertexerp-demo`), choose a strong **Database Password**, and select a region close to your Render deployment (e.g., `us-east-1` / `Oregon`).
3. Once the database is provisioned, go to **Project Settings** $\rightarrow$ **Database**:
   - Locate the **Connection string** section.
   - Under **Transaction Pooler** (Port `6543`) or **Session Pooler** (Port `5432`), copy the URI:
     ```
     postgresql://postgres.[PROJECT_REF]:[YOUR_PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
     ```
4. Enable `pgvector` in the **SQL Editor**:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
5. *(Optional)* Verify Row-Level Security capability:
   ```sql
   SELECT * FROM pg_extension WHERE extname = 'vector';
   ```

---

### Step 2: Provision Upstash Serverless Redis

1. Log in to [Upstash Console](https://console.upstash.com/).
2. Click **Create Database**:
   - Name: `vertexerp-redis-free`
   - Type: Regional (Select the same region as Render/Supabase, e.g. `us-east-1` or `us-west-1`)
   - Eviction: Enable `volatile-lru` or default
3. In the database details dashboard, scroll to **Connect your database**:
   - Select the **ioredis** or **redis-py** tab.
   - Copy the `rediss://` TLS connection string:
     ```
     rediss://default:[YOUR_UPSTASH_PASSWORD]@[YOUR_UPSTASH_HOST].upstash.io:6379
     ```

---

### Step 3: Run Database Migrations (Alembic)

Run the schema migrations to create all multi-tenant tables, indexes, and RLS policies on Supabase:

```bash
# In your local project directory:
export DATABASE_URL="postgresql://postgres.[PROJECT_REF]:[YOUR_PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres"

# Apply all Alembic migrations to head
alembic upgrade head
```

Verify migration status:
```bash
alembic current
```

---

### Step 4: Deploy FastAPI Web Service on Render Free

You can deploy using either the Blueprint file `render.free.yaml` or through the Render Dashboard:

#### Option A: Using `render.free.yaml` Blueprint (Recommended)
1. In Render Dashboard, click **New** $\rightarrow$ **Blueprint**.
2. Connect your GitHub repository (`reegangladis/VertexERP-AI`).
3. Specify the blueprint path: `render.free.yaml`.
4. Render will detect the `vertexerp-api-free` service on the **Free** instance type.
5. In the environment variables prompt, enter your:
   - `DATABASE_URL`: `postgresql://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres`
   - `REDIS_URL`: `rediss://default:[PASSWORD]@[HOST].upstash.io:6379`
   - `ALLOWED_ORIGINS`: `https://[YOUR-VERCEL-APP].vercel.app` (or temporary `https://localhost:3000` until Vercel URL is known)
   - `ALLOWED_HOSTS`: `[YOUR-RENDER-SERVICE-NAME].onrender.com`
6. Click **Apply**.

#### Option B: Manual Web Service Creation
- **Type**: Web Service
- **Runtime**: Docker
- **Instance Type**: Free
- **Health Check Path**: `/health/live`
- **Environment Variables**:
  ```env
  APP_NAME=VertexERP-AI-V2
  APP_ENV=free
  DEPLOYMENT_MODE=free
  WORKER_MODE=embedded
  DATABASE_URL=postgresql://postgres.[REF]:[PASS]@aws-0-[REGION].pooler.supabase.com:6543/postgres
  REDIS_URL=rediss://default:[PASS]@[HOST].upstash.io:6379
  JWT_SECRET_KEY=[GENERATE_RANDOM_32_CHAR_STRING]
  JWT_ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=15
  REFRESH_TOKEN_EXPIRE_DAYS=7
  INTEGRATION_SIGNING_SECRET=[GENERATE_RANDOM_32_CHAR_STRING]
  ALLOWED_ORIGINS=https://[YOUR-VERCEL-APP].vercel.app
  ALLOWED_HOSTS=[YOUR-RENDER-APP].onrender.com
  AI_DEFAULT_PROVIDER=mock
  AI_DEFAULT_MODEL=mock-gpt-4o
  LOG_LEVEL=INFO
  LOG_JSON_FORMAT=true
  RATE_LIMIT_AUTH_PER_MINUTE=10
  RATE_LIMIT_AI_PER_MINUTE=30
  RATE_LIMIT_DEFAULT_PER_MINUTE=120
  ```

---

### Step 5: Deploy Frontend on Vercel Hobby

1. Log in to [Vercel](https://vercel.com/dashboard) and click **Add New...** $\rightarrow$ **Project**.
2. Import your GitHub repository (`reegangladis/VertexERP-AI`).
3. Configure the build settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `./` (or `frontend`)
   - **Build Command**: `cd frontend && npm run build` (or `npm run build` if Root is `frontend`)
   - **Output Directory**: `frontend/dist` (or `dist` if Root is `frontend`)
4. Under **Environment Variables**, add:
   ```env
   VITE_API_URL=https://[YOUR-RENDER-APP].onrender.com
   ```
5. Click **Deploy**.
6. Once deployed, note your assigned Vercel URL (e.g. `https://vertexerp-demo.vercel.app`) and update the `ALLOWED_ORIGINS` environment variable in your Render service settings!

---

## 4. Background Worker Strategy in Free Mode

* **No Dedicated Worker Container Needed**: In standard production, Render requires a paid Background Worker instance ($25/mo). In `$0` Free mode, setting `DEPLOYMENT_MODE=free` and `WORKER_MODE=embedded` activates an asynchronous task pool directly inside the FastAPI ASGI process.
* **Non-Blocking Execution**: Background jobs (report rendering, audit logging, email triggers, scheduled tasks) execute on the async event loop without blocking HTTP request handling.
* **Cron Scheduling**: The embedded cron scheduler evaluates recurring tasks every 60 seconds with distributed locking via Upstash Redis.

---

## 5. Security & Tenant Isolation Guarantees

Even in `$0` Free Deployment mode, VertexERP AI V2 enforces strict multi-tenant boundaries:
1. **PostgreSQL RLS**: All tenant queries require `app.current_tenant_id` context set via PostgreSQL `set_config`. Data leaks between tenants are physically prevented at the database engine level.
2. **CORS & Host Protection**: Wildcard CORS (`*`) and wildcard host headers are rejected at boot time.
3. **High-Entropy Secrets**: Insecure default development keys are rejected by validation invariants.
4. **Sliding-Window Rate Limiting**: Redis-backed rate limiting protects all public authentication and API endpoints against brute force attacks.

---

## 6. Verification and Health Probes

Verify the live deployment using standard HTTP probes:

```bash
# 1. Liveness check
curl -f https://[YOUR-RENDER-APP].onrender.com/health/live

# 2. Readiness check (Verifies Supabase DB & Upstash Redis connectivity)
curl -f https://[YOUR-RENDER-APP].onrender.com/health/ready

# 3. Prometheus telemetry
curl -f https://[YOUR-RENDER-APP].onrender.com/metrics/json
```

---

## 7. Free Tier Operational Gotchas & Limitations

| Provider / Feature | Free Tier Behavior | Recommendation |
| :--- | :--- | :--- |
| **Render Web Service** | Spins down after 15 minutes of inactivity; first request may take 30-50s (cold start). | Normal for $0 demo tier. Add a free uptime monitor (e.g. Better Uptime / Cron-Job.org) to ping `/health/live` every 10 minutes if warm responses are desired. |
| **Supabase Database** | Free tier projects pause after 7 days of inactivity. | Access the dashboard or make an API request once a week to maintain active status. Database size limit is 500 MB. |
| **Upstash Redis** | Free tier limit: 10,000 commands/day. | VertexERP AI V2 automatically uses cached token validations and non-blocking stream reads to stay well within daily limits. |
| **Storage (Cloudflare R2)** | Free tier includes 10 GB storage and 10M read requests/month. | Ideal for file uploads and PDF report storage without egress fees. |

---

## 8. Upgrading to Full Production Architecture

When migrating from Free Demo Mode to enterprise production:
1. Deploy via `render.yaml` using Render Managed PostgreSQL 16 and Managed Redis.
2. Scale API to multiple Uvicorn worker replicas (`--workers 4`).
3. Set `DEPLOYMENT_MODE=production` and `WORKER_MODE=daemon` to spin up the dedicated background worker process (`python -m app.worker`).
4. Connect high-throughput AI providers (OpenAI / Anthropic / Gemini) by supplying your production API keys.
