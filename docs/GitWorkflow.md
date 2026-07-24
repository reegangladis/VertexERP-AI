# Git Workflow & Branching Strategy - VertexERP AI

This guide details the git workflow, branching models, and commit requirements for developers contributing to **VertexERP AI**.

---

## 🌿 Branching Model

We enforce a **Git Flow** strategy containing the following branching categories:

1. **`main`**: Represents production-ready releases. Direct commits are forbidden.
2. **`develop`**: The primary integration branch. All feature branches merge here.
3. **`feature/*`**: Isolated feature development (e.g. `feature/sprint-1.3-foundation-completion`). Created from and merged back into `develop`.
4. **`hotfix/*`**: Immediate patches for production bugs. Created from `main` and merged into both `main` and `develop`.

---

## 📝 Commit Conventions

Commits must follow the **Conventional Commits** standard:

- **`feat(...)`**: A new feature or capability (e.g. `feat(core): implement API response client`).
- **`fix(...)`**: A bug fix (e.g. `fix(logging): resolve file output directory creation`).
- **`docs(...)`**: Documentation adjustments.
- **`refactor(...)`**: Code changes that neither fix a bug nor add a feature.
- **`test(...)`**: Adding or refactoring test suites.

---

## 🔄 Pull Request Lifecycle

Before merging any pull request into `develop` or `main`:
1. Code must be formatted using Black/Prettier and pass Ruff/ESLint quality gates.
2. Local test suites (pytest and Vitest) must pass without warnings.
3. PR must be reviewed and approved by code owners specified in `CODEOWNERS`.
4. Merge using standard squash-merge to keep Git history clean.
