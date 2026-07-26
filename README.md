# VertexERP AI — Enterprise AI Operating System

Welcome to **VertexERP AI**, an enterprise cloud-native ERP platform built to coordinate high-throughput business data, real-time intelligence telemetry, and distributed caching at scale.

This repository represents **Phase 19 (Production Readiness, Performance & Security Hardening)**, delivering enterprise OWASP Top 10 security hardening, HTTP security headers (CSP, HSTS), Circuit Breaker & Bulkhead resilience patterns, database query profiling, disaster recovery RPO/RTO automation, SOC 2 / ISO 27001 / GDPR compliance governance, 6 new database tables, 6 backend API groups, 6 React frontend pages, and automated unit test suites.

---

## 🛠️ Stack Configuration

| Layer | Technology | Version / Standard |
|---|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, TanStack Query | Strict TS, React Router v7 |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Uvicorn | Clean Architecture |
| **Database & Cache** | PostgreSQL 17, Redis 7 | Persistent Volume Mapping |
| **Vector DB** | FAISS, ChromaDB, PgVector | Pluggable Adaptability |
| **ML Studio & Engines** | scikit-learn, XGBoost, LightGBM, CatBoost, TensorFlow, PyTorch, Prophet | Universal Adapter Pattern |
| **XAI & Profiling** | SHAP, LIME, Permutation Importance | Enterprise Explainability |
| **Integration Platform** | API Gateway, Webhook Engine, Event Bus, Queue Engine, Connector Framework | Vendor-Agnostic Hybrid Multi-Cloud |
| **Production Readiness** | CSP, HSTS, Circuit Breaker, Bulkhead, PITR Restore, SOC 2 / GDPR | OWASP Top 10 Hardened |
| **DevOps** | Docker, Docker Compose, GitHub Actions | Multi-stage Compilation |
| **Formatting** | Ruff, Black, ESLint, Prettier | Strict Quality Gates |

---

## 📂 Architecture & Guides

Detailed operational documentation is available under the `docs/` directory:

1. 📘 [Production Readiness Guide](docs/ProductionReadinessGuide.md) — pre-flight deployment scorecard and high availability architecture.
2. 📘 [Security Hardening Guide](docs/SecurityGuide.md) — OWASP Top 10 defenses, CSP, HSTS, account lockouts, and secret rotation.
3. 📘 [Performance Optimization Guide](docs/PerformanceGuide.md) — P95/P99 latency benchmarks, query profiling, and Redis caching.
4. 📘 [Disaster Recovery Guide](docs/DisasterRecoveryGuide.md) — PITR snapshot backups, SHA-256 integrity, RPO (<15m) and RTO (<60m).
5. 📘 [Compliance Guide](docs/ComplianceGuide.md) — SOC 2 Type II, ISO 27001, GDPR right-to-be-forgotten, and HIPAA security controls.
6. 📘 [Integration Guide](docs/IntegrationGuide.md) — API Gateway, Webhooks, Event Bus, Queues, and File Integration.

2. 📘 [Connector Guide](docs/ConnectorGuide.md) — pluggable connectors for ERP, CRM, Payment, Storage, Email, SMS, Messaging, AI, and IdP.
3. 📘 [Webhook Guide](docs/WebhookGuide.md) — HMAC SHA256 signatures, event subscriptions, and exponential retries.
4. 📘 [API Gateway Guide](docs/APIGatewayGuide.md) — routing, versioning, rate limiting, caching, and API keys.
5. 📘 [Workflow Automation Guide](docs/WorkflowAutomationGuide.md) — visual DAG execution engine, step handlers, and resilience.


1. 📘 [AI Copilot Guide](docs/CopilotGuide.md) — multi-tenant sessions isolation, rate limiting, and interface guidelines.
2. 📘 [Prompt Engineering Guide](docs/PromptEngineeringGuide.md) — templates variables, versions control, and sandbox testing.
3. 📘 [Tool Integration Guide](docs/ToolIntegrationGuide.md) — pluggable tool decorator syntax, JSON validation, and RBAC privilege checks.
4. 📘 [RAG Guide](docs/RAGGuide.md) — modular pipeline layers, embedding providers, and vector databases.
2. 📘 [Knowledge Base Guide](docs/KnowledgeBaseGuide.md) — ingestion, multi-format parsing, chunking, and document lifecycle.
3. 📘 [Retrieval Guide](docs/RetrievalGuide.md) — hybrid search scoring, tenant isolation, and RBAC controls.
4. 📘 [ML Studio Guide](docs/MLStudioGuide.md) — datasets, notebooks, experiments, training, evaluation, comparison, explainability, packaging.
2. 📘 [Model Registry Guide](docs/ModelRegistryGuide.md) — model versions, lifecycle stages, and approval sign-off workflows.
3. 📘 [MLOps Guide](docs/mlops/MLOpsGuide.md) — governance workflows, retraining rules, and model lifecycle audits.
4. 📘 [Deployment Routing Guide](docs/mlops/DeploymentGuide.md) — Blue-Green shifting, Canary splits, and version rollbacks.
5. 📘 [Pipeline Orchestration Guide](docs/mlops/PipelineGuide.md) — versioned pipeline templates, verification checks, and console outputs.
6. 📘 [Explainability Guide](docs/ExplainabilityGuide.md) — SHAP, LIME, Permutation Importance, and waterfall prediction decision explainers.

3. 📘 [Inference Guide](docs/InferenceGuide.md) — real-time/batch prediction APIs, latency monitoring, and ground truth feedback loop.
4. 📘 [Data Engineering Guide](docs/DataEngineeringGuide.md) — data warehouse star/snowflake schema, data lake zones, MDM, and quality engine.

2. 📘 [ETL Pipelines Guide](docs/ETLGuide.md) — incremental/full loads, cron scheduling, and pipeline execution logging.
3. 📘 [Feature Store Guide](docs/FeatureStoreGuide.md) — feature groups, registry, offline store datasets, and online cache architecture.
4. 📘 [Business Intelligence Guide](docs/BusinessIntelligenceGuide.md) — enterprise KPI framework and domain analytics engines.
5. 📘 [Dashboard Guide](docs/DashboardGuide.md) — visual widget catalog and drag-and-drop dashboard builder.

3. 📘 [Reporting Guide](docs/ReportingGuide.md) — dynamic report builder, saved presets, and dataset exports.
4. 📘 [System Architecture](docs/Architecture.md) — clean boundary maps, database connections, and data flows.
5. 📘 [Backend Architecture](docs/BackendArchitecture.md) — service, repository, and middleware patterns.
6. 📘 [Manufacturing Guide](docs/ManufacturingGuide.md) — work centers, machines fleet, and maintenance architecture.
4. 📘 [Production Guide](docs/ProductionGuide.md) — shop floor execution, scrap recording, and MRP engine.
5. 📘 [BOM Guide](docs/BOMGuide.md) — multi-level Bill of Materials, versioning, and cost rollup methodology.
6. 📘 [Finance Setup Guide](docs/FinanceGuide.md) — configuration guide for Chart of Accounts, Invoices, Bills & Banking.

6. 📘 [Double-Entry Accounting Guide](docs/AccountingGuide.md) — double-entry ledger posting rules and transaction workflows.
7. 📘 [Financial Reports Guide](docs/FinancialReportsGuide.md) — Trial Balance, Balance Sheet, P&L, Cash Flow, and Aging Reports.
8. 📘 [Entity-Relationship Diagram](docs/ERD.md) — Mermaid database schema associations.

8. 📘 [Sequence Diagrams](docs/SequenceDiagram.md) — Mermaid call sequences.
9. 📘 [Use Case Diagrams](docs/UseCase.md) — actors and authorizations model.
10. 📙 [Coding Standards](docs/CodingStandards.md) — engineering principles.
11. 🗂️ [Folder Structure Map](docs/FolderStructure.md) — monorepo organization layout.
12. 💻 [Local Development Guide](docs/DevelopmentGuide.md) — running services locally without containers.
13. 🐳 [Container Installation Guide](docs/InstallationGuide.md) — building and starting with Docker Compose.
14. 🤝 [Contributing Standards](docs/Contributing.md) — conventional commit rules.

---

## ⚡ Quick Start (Docker Compose)

Launch the complete ecosystem (PostgreSQL, Redis, FastAPI backend, Nginx frontend) with one command:

```bash
# Start all containers in detached mode
docker compose up --build -d
```

### Access Portals
- **Web User Interface**: [http://localhost:3000](http://localhost:3000)
- **API Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Redoc Interface**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Backend Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 🧪 Testing and Quality Control

Run formatting checks and tests from local workspace:

```bash
# Run backend pytest
cd apps/api
pytest

# Format frontend code
cd ../web
npm run format
```
