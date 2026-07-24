# Engineering and Contribution Guidelines - VertexERP AI

Thank you for contributing to VertexERP AI! This document outlines coding standards, branching practices, and PR verification requirements.

## 1. Branch Naming & Commits

We follow standard git practices for branching and commit structure:
- **Feature Branches**: `feature/sprint-X.Y/short-description`
- **Bug Fixes**: `bugfix/sprint-X.Y/short-description`
- **Docs Update**: `docs/short-description`

Use **Conventional Commits**:
- `feat(component): add specific feature` (maps to updates)
- `fix(component): repair database connection` (maps to bug repairs)
- `docs(component): edit contributing layout` (maps to text documentation)
- `test(component): implement endpoint assertions` (maps to pytest cases)

---

## 2. Formatting & Quality Policies

Before submitting code reviews, you are required to validate formatting locally:

### Python Backend Standards
- **Linter**: `ruff check .`
- **Formatter**: `black .`
- **Code standards**: Adhere to SOLID principles, use type-hints everywhere, and isolate queries in the Repositories layer.

### TypeScript Frontend Standards
- **Linter**: `npm run lint`
- **Formatter**: `npm run format`
- **TypeScript**: Strict mode compilation. Clean component separation, avoid utility duplication.

---

## 3. Pull Request Submission Checklist

When opening a Pull Request (PR), ensure:
1. Local virtual environments run all tests (`pytest`) with 100% success.
2. Web static compilations (`npm run build`) complete without errors.
3. No raw connection strings or secrets are left inside the codebase. All configs use environments from `.env` loaded via Pydantic or Vite configs.
4. Clean architecture boundaries are preserved.
