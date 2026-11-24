# VertexERP AI — Windows Local Development & Setup Guide
## Step-by-Step Instructions for Windows 10/11 Environments

**Version:** 2.0.0 Enterprise  
**Platform:** Windows 10 / Windows 11 (PowerShell 5.1 / PowerShell 7)  

---

## 1. Prerequisites

Ensure the following runtimes are installed on your Windows machine:
1. **Python 3.11.x**: [python.org](https://www.python.org/) (ensure "Add Python to PATH" is checked).
2. **Node.js 20.x or 22.x** and **npm**: [nodejs.org](https://nodejs.org/).
3. **PostgreSQL 16**: [enterprisedb.com](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads).
4. **Git for Windows**: [git-scm.com](https://git-scm.com/).

---

## 2. Setting Up Backend (Python FastAPI)

Open **PowerShell** in the repository root (`VertexERP-AI-main`):

### A. Create and Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

*(If script execution is disabled on your system, run: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`)*

### B. Install Python Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### C. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Ensure your local PostgreSQL credentials in `.env` match your local instance:
```env
DATABASE_URL=postgresql+asyncpg://postgres:YourPassword@localhost:5432/vertexerp_dev
ENVIRONMENT=development
DEBUG=true
```

### D. Run Database Migrations & Enterprise Seed
```powershell
# Run Alembic migrations
alembic upgrade head

# Seed Demo Enterprise Tenant, Users, HRMS, CRM, and Workflows
python -m scripts.seed_enterprise_demo
```

### E. Start Backend Dev Server
```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The API is now live at: `http://localhost:8000`  
Swagger API Documentation: `http://localhost:8000/docs`

---

## 3. Setting Up Frontend (React + Vite)

Open a second **PowerShell** window and navigate to `frontend/`:

### A. Install Node Dependencies
```powershell
Set-Location frontend
npm install
```

### B. Start Frontend Dev Server
```powershell
npm run dev
```
The application will launch at: `http://localhost:5173`

---

## 4. Default Enterprise Demo Credentials

Seed script `scripts/seed_enterprise_demo.py` creates the following accounts (Password: `DemoPassword123!`):

| Role | Email | Workspace Experience |
|---|---|---|
| **Super Admin** | `admin@vertexerp.com` | Both Workspaces (Full Administrative Access) |
| **HR Manager** | `hr@vertexerp.com` | Admin HR Management + Approvals Inbox |
| **Sales Manager** | `sales@vertexerp.com` | Salesforce CRM + Opportunity Pipeline + AI Center |
| **Finance Manager**| `finance@vertexerp.com` | Finance Ledger + Quote Approvals + Reports |
| **Employee** | `employee@vertexerp.com`| greytHR Employee Self-Service (ESS) Portal |

---

## 5. Running Automated Tests on Windows

### A. Frontend Tests (Vitest)
```powershell
Set-Location frontend
npx vitest run
```

### B. Backend Tests (Pytest)
```powershell
python -m pytest tests/unit tests/api tests/security tests/test_enterprise_features.py -v
```

---

## 6. Troubleshooting Common Windows Issues

- **ExecutionPolicy Restriction**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` to allow activating the Python virtual environment.
- **Port Conflict (8000 / 5173)**: If port 8000 or 5173 is occupied, run `Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process` or specify `--port 8001`.
- **PostgreSQL Connection Refused**: Verify PostgreSQL service is running in Windows Services (`services.msc` -> `postgresql-x64-16`).
