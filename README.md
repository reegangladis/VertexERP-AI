# VertexERP AI — Enterprise AI Operating System

Welcome to **VertexERP AI**, an enterprise cloud-native ERP platform built to coordinate high-throughput business data, real-time intelligence telemetry, and distributed caching at scale.

This repository represents **Phase 7 (Finance & Accounting Intelligence Platform)**, implementing core clean architecture patterns, double-entry general ledger accounting, chart of accounts, accounts receivable (AR), accounts payable (AP), cash & banking management, employee expenses, budgeting, tax engine, fixed asset depreciation, statutory financial reports (Balance Sheet, P&L, Cash Flow, Trial Balance, AR/AP Aging), and AI readiness data architecture.

---

## 🛠️ Stack Configuration

| Layer | Technology | Version / Standard |
|---|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, TanStack Query | Strict TS, React Router v7 |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Uvicorn | Clean Architecture |
| **Database & Cache** | PostgreSQL 17, Redis 7 | Persistent Volume Mapping |
| **DevOps** | Docker, Docker Compose, GitHub Actions | Multi-stage Compilation |
| **Formatting** | Ruff, Black, ESLint, Prettier | Strict Quality Gates |

---

## 📂 Architecture & Phase 7 Guides

Detailed operational documentation is available under the `docs/` directory:

1. 📘 [System Architecture](docs/Architecture.md) — clean boundary maps, database connections, and data flows.
2. 📘 [Backend Architecture](docs/BackendArchitecture.md) — service, repository, and middleware patterns.
3. 📘 [API Endpoint Index](docs/API.md) — REST APIs and parameters for Finance, Inventory, CRM & HR.
4. 📘 [Database Relational Schema](docs/Database.md) — Finance database tables, GL ledgers, inventory, and HR.
5. 📘 [Finance Setup Guide](docs/FinanceGuide.md) — configuration guide for Chart of Accounts, Invoices, Bills, Banking & Assets.
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
