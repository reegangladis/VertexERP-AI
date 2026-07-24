# VertexERP AI — Enterprise AI Operating System

Welcome to **VertexERP AI**, an enterprise cloud-native ERP platform built to coordinate high-throughput business data, real-time intelligence telemetry, and distributed caching at scale.

This repository represents the release of **Sprint 1.2 (Enterprise Backend Foundation)**, implementing core clean architecture patterns, structured multi-destination logging, custom request-tracing middleware, Redis cache service integration, generic repositories, service layers, and health validations.

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

## 📂 Architecture Guides

Detailed operational documentation is available under the `docs/` directory:

1. 📘 [System Architecture](docs/Architecture.md) — clean boundary maps, database connections, and data flows.
2. 📘 [Backend Architecture](docs/BackendArchitecture.md) — service, repository, and middleware patterns implemented in Sprint 1.2.
3. 📙 [Coding Standards](docs/CodingStandards.md) — engineering principles and rules for Python/Clean architecture.
4. 🗂️ [Folder Structure Map](docs/FolderStructure.md) — monorepo organization layout.
5. 💻 [Local Development Guide](docs/DevelopmentGuide.md) — running services locally without containers.
6. 🐳 [Container Installation Guide](docs/InstallationGuide.md) — building and starting with Docker Compose.
7. 🤝 [Contributing Standards](docs/Contributing.md) — pull request checklists, branching, and conventional commit rules.

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
