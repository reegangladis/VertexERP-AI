# Approval Engine Guide

## Overview

The VertexERP AI **Approval Engine** (Phase 17) provides enterprise-grade approval workflow management supporting single-level, multi-level, conditional, delegated, and auto-escalated approval flows with full audit history.

---

## Approval Lifecycle

```
Created → Pending → Approved (all levels)
               → Rejected
               → Delegated → Pending (new approver)
               → Escalated → Pending (escalation user)
                           → Auto-escalated (SLA breach)
```

---

## Approval Levels

### Single-Level
```json
{
  "requester_id": "user_john",
  "approver_id": "manager_sarah",
  "level": 1,
  "max_levels": 1,
  "title": "Expense Claim $5,000"
}
```

### Multi-Level (3-Level)
```json
{
  "requester_id": "user_john",
  "approver_id": "manager_sarah",
  "level": 1,
  "max_levels": 3,
  "title": "Capital Purchase $125,000",
  "escalation_user_id": "cfo_user"
}
```
The engine advances `level` by 1 after each approval until `level == max_levels`.

---

## Actions

| Action | Trigger | Effect |
|--------|---------|--------|
| `approve` | Approver clicks Approve | Level advances or request fully approved |
| `reject` | Approver clicks Reject | Status → `rejected`, workflow stops |
| `delegate` | Approver delegates to another user | `approver_id` updated, status → `delegated` |
| `escalate` | Manual or SLA-triggered | `approver_id` → escalation user, level +1 |

---

## SLA Auto-Escalation

The engine checks `due_date` against UTC now. Overdue pending requests with a configured `escalation_user_id` are automatically escalated:

```python
await approval_engine.check_sla_escalations(org_id)
```

This is designed to run as a scheduled background task every 15 minutes.

---

## Approval History

Every action is permanently recorded in the `approval_history` table:

| Field | Description |
|-------|-------------|
| `action` | `created`, `approved`, `rejected`, `delegated`, `escalated`, `auto_escalated` |
| `actor_id` | User ID who performed the action |
| `comments` | Free-text justification |
| `metadata_json` | Optional structured context |

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/approvals/` | Create approval request |
| `GET` | `/api/v1/approvals/` | List approvals |
| `GET` | `/api/v1/approvals/pending/{approver_id}` | Pending for approver |
| `GET` | `/api/v1/approvals/{id}` | Get approval detail |
| `POST` | `/api/v1/approvals/{id}/action` | Process action (approve/reject/delegate/escalate) |
| `GET` | `/api/v1/approvals/{id}/history` | Get approval audit trail |
| `POST` | `/api/v1/approvals/escalate-sla` | Auto-escalate SLA breaches |

---

## Integration with Workflow Engine

The `approval` node type within a workflow automatically pauses execution and creates an `ApprovalRequest`. Upon approval, the workflow execution resumes at the next step.

```json
{
  "type": "approval",
  "data": {
    "label": "Finance Director Approval",
    "config": {
      "approver_role": "finance_director",
      "max_levels": 2,
      "due_hours": 48
    }
  }
}
```
