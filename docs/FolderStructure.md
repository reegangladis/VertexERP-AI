# Monorepo File Map - VertexERP AI

This document maps the repository file tree structure for Sprint 1.1 (Project Foundation).

```
VertexERP-AI/
├── .github/                      # CI/CD Workflows
│   └── workflows/
│       ├── backend.yml           # Backend Python Ruff/Pytest check
│       └── frontend.yml          # Frontend TypeScript build/eslint check
├── apps/                         # Modular Services
│   ├── api/                      # Backend API (Python, FastAPI)
│   │   ├── app/                  # Application Logic
│   │   │   ├── api/              # Routers and Endpoints
│   │   │   ├── core/             # Configuration & Logging
│   │   │   ├── database/         # Postgres Engine & Redis Clients
│   │   │   ├── middleware/       # Exception handlers & CORS
│   │   │   ├── models/           # SQLAlchemy Declarative Models
│   │   │   ├── repositories/     # Repository query abstractions
│   │   │   ├── schemas/          # Pydantic data schemas
│   │   │   ├── services/         # Business domain layers
│   │   │   ├── tests/            # Pytest test cases
│   │   │   └── utils/            # Helper utilities
│   │   ├── alembic/              # Database schema migrations
│   │   ├── requirements.txt      # Python dependencies
│   │   └── pyproject.toml        # Ruff/Black formatter setups
│   └── web/                      # Frontend Application (React, Vite, TS)
│       ├── src/
│       │   ├── components/       # Visual buttons and UI modules
│       │   ├── hooks/            # Custom hooks (useTheme)
│       │   ├── layouts/          # Root page grid layouts
│       │   ├── pages/            # Page routers (Landing, Dashboard)
│       │   ├── services/         # TanStack Query API fetch actions
│       │   └── styles/           # Global Tailwind and theme configurations
│       ├── package.json          # Node dependencies & build tasks
│       ├── tsconfig.json         # TypeScript compiler configurations
│       └── vite.config.ts        # Vite routing & compiler adjustments
├── docker/                       # Docker Compilation Files
│   ├── Dockerfile.api            # Multi-stage production FastAPI image
│   └── Dockerfile.web            # Multi-stage production Nginx/React image
├── docs/                         # Architecture & Operation Guides
│   ├── Architecture.md           # Structural design maps
│   ├── FolderStructure.md        # File map overview
│   ├── DevelopmentGuide.md       # Running project locally
│   ├── InstallationGuide.md      # Launching via Docker-compose
│   └── Contributing.md           # Engineering guidelines
├── packages/
│   └── shared/                   # Shared configurations (placeholder)
├── README.md                     # Central entry guide
├── docker-compose.yml            # System orchestration schema
├── .env.example                  # Environment properties template
└── .gitignore                    # Version control ignore lists
```
