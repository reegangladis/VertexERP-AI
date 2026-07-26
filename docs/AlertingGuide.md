# Alerting Guide - VertexERP AI

This guide describes the alarm rules, severity states, and triage procedures in the VertexERP AI Monitoring & Observability Platform.

## Alerting Incident Workflow

1. **Breach Detected**: Performance metrics are matched against threshold limits.
2. **Alert Triggered**: If breached, the platform creates an `Alert` with state `active`.
3. **Escalation Notification**: Operations staff receives email/Slack notifications (simulated escalation route).
4. **Triage**: Operators can acknowledge the alert (shifting state to `acknowledged`) to take ownership.
5. **Resolution**: Once the resource returns to safe parameters, the state transitions to `resolved`.

---

## Alarm Severity Definitions

- **Critical**: Vital components offline or performance severely degraded (e.g. CPU > 85%, database offline). Requires immediate SRE callout.
- **Warning**: Metrics outside normal parameters (e.g. API latency > 2000ms, RAG retrieval score < 0.80).
- **Info**: Discrete platform events, e.g. system upgrades or config adjustments.

---

## Triage Control REST API

### Acknowledge Alert

- **Endpoint**: `PUT /api/v1/observability/alerts/{alert_id}`
- **Headers**:
  - `Content-Type: application/json`
  - `Authorization: Bearer <JWT_TOKEN>`
- **Payload**:
```json
{
  "status": "acknowledged",
  "description": "Investigating high API gateway processing latencies."
}
```

### Resolve Alert

- **Endpoint**: `PUT /api/v1/observability/alerts/{alert_id}`
- **Payload**:
```json
{
  "status": "resolved",
  "description": "Database pool size increased; CPU loads returned to safe baseline values."
}
```
