# Pluggable Tool Integration Guide

This guide explains how to define, decorate, register, and configure pluggable tools within the **VertexERP AI Copilot Platform**.

---

## 🔌 Decorator Registration Syntax

The platform features a Python decorator-based registry located in `app.services.copilot.tools`. Decorators automatically handle type mapping, parameter descriptions, and permissions mapping.

### Example Registration
```python
from app.services.copilot.tools import registry
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

@registry.register(
    name="get_stock_level",
    description="Query current inventory stock counts and warehouse location mappings.",
    parameters_schema={
        "type": "object",
        "properties": {
            "product_sku": {"type": "string", "description": "SKU code or Product ID."}
        },
        "required": ["product_sku"]
    },
    required_role="inventory.view"
)
async def get_stock_level(db: AsyncSession, org_id: Any, product_sku: str) -> Dict[str, Any]:
    # Custom business logic / database queries
    return {
        "sku": product_sku,
        "total_quantity": 250,
        "status": "synchronized"
    }
```

---

## 🔍 Validation Schemas (JSON Schema)

Every tool must declare a `parameters_schema` in standard JSON Schema format:
- **Type**: Must be `"object"`.
- **Properties**: Inner object keys mapping to function argument names, specifying their types (e.g., `"string"`, `"integer"`, `"boolean"`, `"array"`) and description fields.
- **Required**: List of required argument keys that must be supplied by the LLM caller.

During chat orchestration, the system parses the LLM's suggested tool parameters and validates them against the JSON Schema to mitigate execution errors.

---

## 🔒 Security & RBAC Mapping

- **Role Constraints**: By declaring a `required_role` attribute (e.g. `"hr.view"`), you prevent unauthorized executions.
- **Middleware Check**: The `CopilotService` evaluates the user's active mapped roles. If the user doesn't possess the required role, the execution fails with a permission warning.
- **Multi-Tenant DB Access**: Tool handlers must accept `db` (AsyncSession), `org_id` (current tenant ID), and `user_id` as context parameters to enforce PostgreSQL sandbox isolation.
