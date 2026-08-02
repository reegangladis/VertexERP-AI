# Testing Guide - VertexERP AI

This guide contains instructions for running, writing, and automating tests across backend and frontend workspaces.

---

## 🐍 Backend Test Suite (FastAPI & pytest)

The Python test files are organized under `apps/api/app/tests/`:
- **`unit/`**: Verifies isolated helper structures and mathematical utilities.
- **`integration/`**: Verifies API endpoints using mock transactions for database and Redis.

### Run Pytest
To run the backend test suite, activate your local virtual environment:

```bash
cd apps/api
.\venv\Scripts\activate
pytest
```

---

## ⚛️ Frontend Test Suite (React & Vitest & RTL)

The frontend test files are located under `apps/web/src/tests/`:
- **`setup.ts`**: Initial JSDOM setups mocking window API methods (like `matchMedia`).
- **`unit/`**: Verifies atomic UI elements, theme triggers, and layout boundaries.

### Run Vitest
Run Vitest checks inside the frontend workspace directory:

```bash
cd apps/web
npm run test
```

---

## 🧪 Testing Best Practices

1. **Keep Tests Async-Safe**: Backend tests must use `@pytest.mark.asyncio`, and frontend tests should use `async/await` matching React Testing Library actions.
2. **Isolate Database State**: Never run integration tests against a live database. Mock session parameters and use Vitest mock functions (`vi.mock`) to isolate services.
3. **Trace Errors**: Use logging file outputs (`apps/api/logs/`) to track failed API states during local integration tests.
