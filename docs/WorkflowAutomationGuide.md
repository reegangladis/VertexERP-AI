# Workflow Automation Guide

## Overview

The VertexERP AI **Enterprise Workflow Automation Platform** (Phase 17) provides a production-ready, engine-agnostic workflow management system supporting visual workflow design, complex conditional execution, AI-integrated step actions, and enterprise-grade monitoring.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Enterprise Workflow Platform                        │
│                                                                     │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │ Visual Designer│  │ Rule Engine  │  │   Approval Engine    │    │
│  │ (Drag-n-Drop)  │  │ (Expression) │  │ (Multi-level)        │    │
│  └────────┬───────┘  └──────┬───────┘  └──────────┬───────────┘    │
│           │                 │                       │                │
│           └─────────────────┴───────────────────────┘               │
│                             │                                        │
│                    ┌────────▼────────┐                              │
│                    │  Workflow Engine │                              │
│                    │   (DAG Executor) │                              │
│                    └────────┬────────┘                              │
│                             │                                        │
│     ┌───────────┬───────────┼───────────┬──────────────┐            │
│     │           │           │           │              │            │
│ ┌───▼────┐ ┌───▼────┐ ┌───▼────┐ ┌───▼────┐ ┌───────▼────┐       │
│ │Trigger │ │Action  │ │Condition│ │Approval│ │AI (Copilot,│       │
│ │Handler │ │Handler │ │Handler │ │Handler │ │RAG, ML)    │       │
│ └────────┘ └────────┘ └────────┘ └────────┘ └────────────┘       │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │            Scheduler Engine (Cron / Recurring / One-Time)    │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Visual Workflow Designer

### Canvas
The designer provides a drag-and-drop canvas interface built on SVG edge rendering with:
- **Node Palette** — 8 node types
- **Properties Panel** — per-node configuration
- **Edge Rendering** — bezier-curved SVG connectors
- **Draft / Publish** controls

### Node Types

| Node Type | Description |
|-----------|-------------|
| `trigger` | Entry point of workflow |
| `action` | Executes an operation |
| `condition` | If/Else or Switch branching |
| `approval` | Human-in-the-loop approval |
| `ai_copilot` | Runs AI Copilot prompt |
| `rag_search` | Queries RAG knowledge base |
| `ml_prediction` | Runs ML model inference |
| `external_api` | Calls external REST endpoint |

### Graph Definition Schema
```json
{
  "nodes": [
    {
      "id": "n1",
      "type": "trigger",
      "position": { "x": 60, "y": 180 },
      "data": {
        "label": "Manual Trigger",
        "config": { "trigger_type": "manual" }
      }
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "n1",
      "target": "n2",
      "condition_value": "true"
    }
  ]
}
```

---

## Triggers

| Trigger Type | Description |
|--------------|-------------|
| `manual` | User-initiated via API or UI |
| `rest_api` | Webhook POST to execution endpoint |
| `database` | DB event/change listener |
| `scheduled` | Cron-based trigger via Scheduler |
| `webhook` | External webhook delivery |
| `file_upload` | Document upload event |
| `erp_event` | Internal ERP lifecycle event |
| `ai_event` | AI Copilot / ML model event |

---

## Execution Engine (DAG)

The workflow engine executes a **Directed Acyclic Graph (DAG)** of step nodes.

### Execution Lifecycle
```
PENDING → RUNNING → COMPLETED
                  → FAILED → (retry) → RUNNING
                  → CANCELLED
```

### Conditions
- **If/Else** — compares field value against expected, sets `__branch__` = `"true"` | `"false"`
- **Switch** — branches on field value as string key
- **Parallel** — simultaneously visits multiple successor nodes
- **Retry** — each node supports `max_retries` with exponential backoff

### Error Handling
Failures at any step:
1. Check `retry_count < max_retries`
2. If retries exhausted → mark step `failed`, log error
3. Mark execution `failed` with full error context

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/workflows/` | Create workflow |
| `GET` | `/api/v1/workflows/` | List workflows |
| `GET` | `/api/v1/workflows/{id}` | Get workflow |
| `PATCH` | `/api/v1/workflows/{id}` | Update workflow |
| `DELETE` | `/api/v1/workflows/{id}` | Delete workflow |
| `POST` | `/api/v1/workflows/{id}/execute` | Trigger execution |
| `POST` | `/api/v1/workflows/{id}/versions` | Create version |
| `POST` | `/api/v1/workflows/{id}/versions/{vid}/publish` | Publish version |
| `GET` | `/api/v1/workflows/{id}/export` | Export workflow |
| `POST` | `/api/v1/workflows/import` | Import workflow |
| `POST` | `/api/v1/workflow-executions/{id}/cancel` | Cancel execution |
| `POST` | `/api/v1/workflow-executions/{id}/retry` | Retry execution |

---

## AI Integration

Workflow nodes directly integrate with VertexERP AI Platform:

- **`ai_copilot` node** — Runs Enterprise AI Copilot prompts within workflow context
- **`rag_search` node** — Queries Enterprise RAG knowledge base for context-aware data retrieval
- **`ml_prediction` node** — Executes ML model inference and injects predictions into workflow context

---

## Security

| Feature | Implementation |
|---------|---------------|
| Tenant Isolation | All tables enforce `organization_id` FK |
| RBAC | Endpoints require role-based access |
| Audit Logging | Workflow executions and approval actions logged |
| Execution Context | Input/output payloads encrypted in transit |
