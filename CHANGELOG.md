# Changelog - VertexERP AI

All notable changes to the **VertexERP AI** project will be documented in this file.

The project follows [Semantic Versioning](https://semver.org/).

---

## [0.3.0] - 2026-07-24 (Sprint 1.3 - Enterprise Foundation Completion)

### Added
- **Design System Styles**: Added `variables.css` centralizing spacing, typography, elevations, and HSL colors for Dark/Light modes.
- **Global Context Stores**: Set up React Context Providers in the `store/` directory:
  - `ThemeProvider` for Dark/Light class toggles.
  - `UIProvider` managing Sidebar expand/collapse states and Modal controls.
  - `NotificationProvider` handling generic toast alert notifications.
  - `SettingsProvider` governing API base URLs and feature flags.
- **Axios client wrapper**: Configured `apiClient.ts` with custom request interceptors generating `X-Request-ID` tracing tokens, and response interceptors mapping server errors.
- **Error Boundaries**: Implemented a global React `ErrorBoundary` displaying formatted details during UI rendering failures.
- **Static Route Pages**: Created 404 (Not Found), 500 (Internal Error), Maintenance, and Unauthorized fallback screens.
- **Vitest Testing**: Formed Vitest JSDOM environment in `apps/web/` and wrote tests for `ThemeToggle`, `LandingPage`, and `NotFound` pages.
- **GitHub Configurations**: Created CODEOWNERS files, Dependabot schedules, issue bug/feature template worksheets, pull request templates, and branching strategies.

### Changed
- **TS Strict Mode**: Set `"strict": true` in `tsconfig.app.json`.
- **Ruff Linting**: Configured `pyproject.toml` with `isort` settings to group imports natively.
- **Docker Health Checks**: Added container healthchecks to `Dockerfile.web` and updated `docker-compose.yml` to check container health.

---

## [0.2.0] - 2026-07-24 (Sprint 1.2 - Enterprise Backend Foundation)

### Added
- **Custom Exceptions**: Formed custom exception classes (`NotFoundException`, `ValidationException`, `ConflictException`, etc.) mapping directly to standard HTTP status codes.
- **Standardized API Responses**: Serialized all endpoint data payloads inside a generic response envelope.
- **Logging separations**: Configured multi-destination logging sending console logs to stdout, and operational logs to separate rotating file targets (`app.log`, `error.log`, `access.log`).
- **ASGI Middlewares**: Registered Request ID tracers (`X-Request-ID`), process time calculations (`X-Process-Time`), security headers, and HTTP request access auditors.
- **Database Model Mixins**: Added UUID primary keys, timezone-aware UTC timestamps, and soft deletion mixins.
- **Redis connection client**: Developed connection pool controllers supporting ping healthchecks and automatic JSON serialization/deserialization.
- **Generic Abstractions**: Developed BaseRepository and BaseService classes containing reusable CRUD queries, dynamic filter/sorting mappings, and hooks.
- **Pytest Reorganization**: Restructured test cases into `unit/` and `integration/` suites.

---

## [0.1.0] - 2026-07-24 (Sprint 1.1 - Project Foundation)

### Added
- **Project Structure**: Set up monorepo workspaces containing modular directories: `apps/api` (FastAPI) and `apps/web` (React 19).
- **FastAPI backend**: Configured Uvicorn, routes prefixing, and health check endpoints.
- **Database migrations**: Configured Alembic and PostgreSQL engines.
- **Frontend SPA**: Configured React with Vite and Tailwind CSS.
- **DevOps**: Wrote multi-stage `Dockerfile.api` and `Dockerfile.web` environments coordinated in `docker-compose.yml`.
