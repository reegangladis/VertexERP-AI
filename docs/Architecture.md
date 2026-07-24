# Architectural Design Document - VertexERP AI

This document specifies the software architecture design for **VertexERP AI** (Enterprise AI Operating System), outlining layers, communication patterns, and design patterns.

## Technical Architecture Overview

VertexERP AI utilizes a **Monorepos (Single Repository) Architecture** housing modular services under decoupled structures.

```mermaid
graph TD
    Client[Browser React 19 SPA] -->|HTTP / JSON| API[FastAPI Gateway]
    API -->|Async Engine| DB[(PostgreSQL 17)]
    API -->|Redis Protocol| Cache[(Redis 7 Cache)]
    
    subgraph Frontend [React Web Client]
        Client
    end
    
    subgraph Backend [FastAPI Clean Architecture Core]
        API
    end
```

---

## Backend Clean Architecture

The backend project structure enforces a decoupled directory boundary separation to isolate operational logic, configurations, and communication routes:

- **`app/core/`**: Configuration management (via `pydantic-settings` Settings class validating environments), context tracking (`context.py`), dependency injection (`dependencies.py`), custom exceptions (`exceptions.py`), and structured logging (`logging.py`).
- **`app/api/`**: Router definitions and versioned endpoints (`health.py`, `version.py`). All responses are serialized using standard JSON `APIResponse` schemas.
- **`app/database/`**: Database connection pool setups, abstract `BaseModel` containing UUID and timezone-aware timestamp mixins, soft delete capabilities (`base.py`), and connection managers/caching APIs via `RedisService` (`redis.py`).
- **`app/middleware/`**: CORS settings, custom middlewares (Request ID, Processing Time, Access Logging, and Security Headers), and global exception interrupters formatting error responses.
- **`app/repositories/`**: Generic `BaseRepository` implementing async CRUD operations, dynamic sorting, pagination, and filtering abstractions.
- **`app/services/`**: Generic `BaseService` managing service logic, validation hooks, and repository triggers.
- **`app/schemas/`**: Pydantic v2 schemas validating request parameters, documenting endpoints, and defining response structures (`response.py`).
- **`app/utils/`**: Utilities for dates, UUID validation, pagination metadata, standard responses, and validation checks.
- **`app/models/`**: SQLAlchemy declarative databases and table schemas.

---

## Frontend Monolith-SPA Design

The client panel uses a modular Component-Layout-Page separation:

- **`src/app/`**: Global runtime setups (context engines, providers).
- **`src/components/`**: Atomic visual features (buttons, forms, indicator badges, charts).
- **`src/layouts/`**: Core wireframe grids (Navbar headers, side navigations, footers).
- **`src/pages/`**: Complete router page views (Overview, dynamic workspace placeholders, 404).
- **`src/services/`**: API fetching clients built with TanStack Query.
- **`src/hooks/`**: Specialized React hooks (e.g. `useTheme` managing light/dark preferences).
