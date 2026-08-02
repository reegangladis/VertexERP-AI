# Coding Standards - VertexERP AI

This document establishes the engineering rules and coding standards for development in **VertexERP AI**.

---

## 🏛️ Clean Architecture & SOLID Principles

All backend modifications must follow clean architecture guidelines to keep logic separated:

- **Single Responsibility (SRP)**: Each class, utility, router, or repository must serve exactly one purpose. Separate database access (Repository) from business rules (Service) and serialization schemas (Pydantic models).
- **Open/Closed (OCP)**: Extend behavior by subclassing rather than altering tested base classes. Use generic models (`BaseRepository` and `BaseService`).
- **Interface Segregation**: Keep route signatures, service dependencies, and database schemas clean. Depend on generic wrappers where possible.
- **Dependency Inversion (DIP)**: Use FastAPI `Depends` for dependency injection. Do not directly instantiate database sessions or config clients inside controllers.

---

## 🏷️ Python Development Conventions

### 1. Strict Type Hints
Type annotations are **mandatory** for all function signatures, parameters, class members, and variables. Avoid `Any` where possible.
```python
# Correct
async def get_records(db: AsyncSession, *, skip: int = 0) -> list[ModelType]:
    ...
```

### 2. Standardized Responses
Every API endpoint route **must** return standardized responses wrapped in the `APIResponse` envelope. Do not return raw entities or models.
```python
# Correct
@router.get("", response_model=APIResponse[DataModel])
async def read_item() -> APIResponse[DataModel]:
    return APIResponse(success=True, message="Data found", data=item)
```

### 3. Exception Handling
Never return custom error codes inside successful responses. Raise custom HTTP exceptions (`ValidationException`, `NotFoundException`, etc.) and let the global exception interceptor map them to a standardized response.
```python
# Correct
if not item:
    raise NotFoundException(message=f"Item with id {item_id} not found")
```

### 4. Database Persistence Patterns
- Always inherit from `BaseModel` for new SQLAlchemy model definitions to get UUID keys and UTC timestamps automatically.
- Inherit from `SoftDeleteMixin` if records must be soft-deleted instead of hard-deleted.
- Write CRUD operations in repository classes subclassing `BaseRepository`. Do not write raw SQL queries or DB session calls inside endpoints or service components.

---

## 🧪 Testing Guidelines

- Write isolated **Unit Tests** under `app/tests/unit/` for utility routines, configurations, and standalone exceptions.
- Write **Integration Tests** under `app/tests/integration/` to verify HTTP route pipelines, controller endpoints, headers, and dependency overrides.
- Use mock database sessions (`mock_db_session`) and mock Redis services in test assertions to avoid dependency on database availability.
- All tests must be async-compatible using `@pytest.mark.asyncio`.

---

## 🧹 Formatting & Style Standards

Code files must pass the strict style gates checked in CI/CD pipeline runs:

1. **Formatter (Black)**: Set to an 88-character line limit. Run black formatting before commiting:
   ```bash
   black .
   ```
2. **Linter (Ruff)**: Linting rules map to `pyproject.toml` configurations. Verify there are no lint issues:
   ```bash
   ruff check .
   ```
