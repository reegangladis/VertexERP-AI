# Operations & Incident Response Runbook — VertexERP AI

## Overview
This runbook guides Site Reliability Engineers (SRE) and Cloud Operations teams through operational procedures, incident triage (P1-P4), and MTTR SLAs.

---

## Incident Severity Matrix

| Severity | Impact | SLA MTTR Target | Action Required |
|----------|--------|-----------------|-----------------|
| **P1 Critical** | Global Outage / Multi-Region failure | < 15 minutes | Immediate SRE page & Failover execution |
| **P2 High** | Regional degradation / High latency | < 30 minutes | Scale HPA pods & Flush cache pool |
| **P3 Medium** | Single non-critical service error | < 4 hours | Investigate logs & Apply hotfix |
| **P4 Low** | Cosmetic / Non-impacting anomaly | < 24 hours | Log ticket for next sprint |
