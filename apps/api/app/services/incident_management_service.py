import uuid
from datetime import datetime, UTC
from typing import Dict, Any, List, Optional


class IncidentManagementService:
    """Operational Incident Response, MTTR Telemetry, and Runbook Automation Engine."""

    def __init__(self):
        self._incidents: List[Dict[str, Any]] = [
            {
                "id": str(uuid.uuid4()),
                "incident_number": "INC-2026-0042",
                "title": "API Gateway Connection Spike in EU Region",
                "severity": "P2",
                "status": "RESOLVED",
                "affected_services": ["api_gateway", "redis_cluster"],
                "mttr_minutes": 14.5,
                "root_cause": "Transient Redis cluster connection pool exhaustion during peak traffic",
                "runbook_executed": "RB-OPS-042: Redis Connection Pool Scaling & Flush",
                "assigned_oncall": "SRE_Duty_Engineer_01",
                "created_at": datetime.now(UTC).isoformat(),
                "resolved_at": datetime.now(UTC).isoformat(),
            }
        ]

    def log_incident(
        self,
        title: str,
        severity: str = "P2",
        affected_services: Optional[List[str]] = None,
        root_cause: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Logs an operational incident and assigns an on-call SRE engineer."""
        inc_num = f"INC-2026-{len(self._incidents) + 101:04d}"
        incident_record = {
            "id": str(uuid.uuid4()),
            "incident_number": inc_num,
            "title": title,
            "severity": severity,
            "status": "INVESTIGATING",
            "affected_services": affected_services or ["core_api"],
            "mttr_minutes": 0.0,
            "root_cause": root_cause,
            "runbook_executed": f"RB-OPS-AUTO: Triggered for {severity}",
            "assigned_oncall": "OnCall_SRE_Team",
            "created_at": datetime.now(UTC).isoformat(),
            "resolved_at": None,
        }
        self._incidents.append(incident_record)
        return incident_record

    def resolve_incident(self, incident_number: str, mttr_minutes: float, root_cause: str) -> Dict[str, Any]:
        """Marks an operational incident as RESOLVED and records final MTTR."""
        inc = next((i for i in self._incidents if i["incident_number"] == incident_number), None)
        if not inc:
            return {"error": f"Incident {incident_number} not found"}

        inc["status"] = "RESOLVED"
        inc["mttr_minutes"] = mttr_minutes
        inc["root_cause"] = root_cause
        inc["resolved_at"] = datetime.now(UTC).isoformat()
        return inc

    def get_mttr_summary(self) -> Dict[str, Any]:
        """Returns overall MTTR operational metrics."""
        resolved = [i for i in self._incidents if i["status"] == "RESOLVED"]
        avg_mttr = sum(i["mttr_minutes"] for i in resolved) / len(resolved) if resolved else 0.0

        return {
            "total_incidents_logged": len(self._incidents),
            "open_incidents": len([i for i in self._incidents if i["status"] != "RESOLVED"]),
            "average_mttr_minutes": round(avg_mttr, 1),
            "target_mttr_sla_minutes": 30.0,
            "mttr_sla_met": avg_mttr <= 30.0,
        }
