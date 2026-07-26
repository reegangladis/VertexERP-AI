# Rule Engine Guide

## Overview

The VertexERP AI **Business Rule Engine** (Phase 17) evaluates logical condition trees against runtime context data to drive automated decisions within the Workflow Automation Platform.

---

## Rule Structure

```json
{
  "name": "High-Value Invoice Alert",
  "rule_group": "finance",
  "priority": 1,
  "is_active": true,
  "conditions_json": {
    "logical_operator": "AND",
    "conditions": [
      { "field": "invoice.amount", "operator": ">=", "value": 50000 },
      { "field": "invoice.status", "operator": "==", "value": "pending" }
    ]
  },
  "actions_json": {
    "actions": ["send_email", "create_task", "escalate_approval"]
  }
}
```

---

## Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `==` | Equals | `"status" == "pending"` |
| `!=` | Not equals | `"type" != "internal"` |
| `>` | Greater than | `"amount" > 10000` |
| `<` | Less than | `"days" < 30` |
| `>=` | Greater than or equal | `"score" >= 80` |
| `<=` | Less than or equal | `"retries" <= 3` |
| `in` | Value in list | `"role" in ["admin", "cfo"]` |
| `not_in` | Value not in list | `"status" not_in ["closed"]` |
| `contains` | String contains | `"name" contains "Corp"` |
| `not_contains` | String does not contain | `"email" not_contains "@test"` |
| `starts_with` | String prefix | `"code" starts_with "INV-"` |
| `ends_with` | String suffix | `"email" ends_with "@company.com"` |
| `matches` | Regex match | `"phone" matches "^\\+[0-9]+"` |
| `is_null` | Value is null | `"approved_at" is_null` |
| `is_not_null` | Value is not null | `"manager_id" is_not_null` |

---

## Logical Groups

### AND Group (all must match)
```json
{
  "logical_operator": "AND",
  "conditions": [
    { "field": "amount", "operator": ">=", "value": 10000 },
    { "field": "status", "operator": "==", "value": "pending" }
  ]
}
```

### OR Group (any must match)
```json
{
  "logical_operator": "OR",
  "conditions": [
    { "field": "role", "operator": "==", "value": "cfo" },
    { "field": "role", "operator": "==", "value": "ceo" }
  ]
}
```

### Nested Groups
```json
{
  "logical_operator": "AND",
  "conditions": [
    { "field": "status", "operator": "==", "value": "active" }
  ],
  "groups": [
    {
      "logical_operator": "OR",
      "conditions": [
        { "field": "amount", "operator": ">=", "value": 50000 },
        { "field": "priority", "operator": "==", "value": "urgent" }
      ]
    }
  ]
}
```

---

## Dot-Notation Field Resolution

Fields support nested property paths:

```
"invoice.line_items.total"  →  context["invoice"]["line_items"]["total"]
```

---

## Rule Priority

Rules within a group are evaluated in ascending priority order (1 = highest). The engine evaluates all active rules and collects all matched rule actions.

---

## Rule Testing

Test a specific rule against sample data without affecting production:

```bash
POST /api/v1/workflow-rules/{rule_id}/test
{
  "invoice": {
    "amount": 75000,
    "status": "pending"
  }
}
```

Response:
```json
{
  "rule_id": "...",
  "rule_name": "High-Value Invoice Alert",
  "matched": true,
  "triggered_actions": ["send_email", "create_task", "escalate_approval"]
}
```

---

## Rule Evaluation in Workflows

Use the `condition` node type in the Workflow Designer to trigger a rule group evaluation:

```json
{
  "type": "condition",
  "data": {
    "config": {
      "condition_type": "if_else",
      "field": "invoice.amount",
      "operator": ">=",
      "value": 50000
    }
  }
}
```

Alternatively, evaluate an entire rule group using the `evaluate` endpoint:

```bash
POST /api/v1/workflow-rules/evaluate
{
  "rule_group": "finance",
  "context_data": {
    "invoice": { "amount": 75000, "status": "pending" }
  }
}
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/workflow-rules/` | Create rule |
| `GET` | `/api/v1/workflow-rules/` | List rules |
| `GET` | `/api/v1/workflow-rules/groups` | List rule groups |
| `GET` | `/api/v1/workflow-rules/{id}` | Get rule |
| `PATCH` | `/api/v1/workflow-rules/{id}` | Update rule |
| `DELETE` | `/api/v1/workflow-rules/{id}` | Delete rule |
| `POST` | `/api/v1/workflow-rules/evaluate` | Evaluate rules against context |
| `POST` | `/api/v1/workflow-rules/{id}/test` | Test single rule |
