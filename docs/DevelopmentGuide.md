# Local Development Guide - VertexERP AI

This guide contains step-by-step sequences for configuring, running, and testing the backend and frontend services locally on your machine without relying on container environments.

## Prerequisites
- Python 3.12
- Node.js 22 LTS or newer
- Running instances of PostgreSQL and Redis locally

---

## 1. Backend Core Setup (`apps/api/`)

Navigate to the backend directory and establish a Python virtual environment:

```bash
cd apps/api
python -m venv venv
```

Activate the environment:
- **Windows (PowerShell)**: `.\venv\Scripts\Activate.ps1`
- **Linux/macOS**: `source venv/bin/activate`

Install dependencies:
```bash
pip install -r requirements.txt
```

Set up local configurations (if database endpoints are different than `docker-compose` settings, adjust `.env` file):
```bash
# Verify .env configurations at project root match your local DB
```

Run database migrations (using Alembic):
```bash
alembic upgrade head
```

Start the FastAPI application via Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```
API docs will load at: `http://localhost:8000/docs`

---

## 2. Frontend Web Setup (`apps/web/`)

Navigate to the frontend folder and install dependencies:
```bash
cd apps/web
npm install
```

Configure local environment inputs (optional):
- By default, the app resolves to `http://localhost:8000` for backend communication. If your API runs elsewhere, copy `.env.example` into `.env` under `apps/web/` and define `VITE_API_URL`.

Run the Vite dev server:
```bash
npm run dev
```
The interface will load at: `http://localhost:3000`

---

## 3. Code Quality Actions

### Backend Quality (Ruff & Black)
Format code:
```bash
black .
```

Check lint violations:
```bash
ruff check .
```

### Frontend Quality (ESLint & Prettier)
Validate lints:
```bash
npm run lint
```

Format code:
```bash
npm run format
```

---

## 4. Run Test Suites
Inside `apps/api` with active virtual environment:
```bash
pytest
```
This runs the system's test suite, including:
- **Unit Tests (`app/tests/unit/`)**: Verifying utility functions, helper methods, and isolated exceptions.
- **Integration Tests (`app/tests/integration/`)**: Verifying FastAPI endpoints, route parameters, response payloads, database state mocks, and Redis service health.

Logs will be written to `apps/api/logs/` (`app.log`, `error.log`, and `access.log`).

