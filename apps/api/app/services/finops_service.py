import uuid
from datetime import UTC, datetime
from typing import Any


class FinOpsService:
    """FinOps Cloud Cost Optimization & Budget Monitoring Engine."""

    def __init__(self):
        self._current_month = datetime.now(UTC).strftime("%Y-%m")

    def get_monthly_cost_summary(self) -> dict[str, Any]:
        """Returns FinOps cloud cost breakdown and budget metrics."""
        total_cost = 38450.00
        budget = 50000.00
        utilized_percent = round((total_cost / budget) * 100.0, 1)

        service_breakdown = {
            "kubernetes_eks": 14200.00,
            "postgresql_rds": 11500.00,
            "redis_elasticache": 3800.00,
            "s3_cloud_storage": 2450.00,
            "data_transfer_egress": 4500.00,
            "security_waf_kms": 2000.00,
        }

        recommendations = [
            "Convert 8 EKS worker nodes to AWS Savings Plans / Reserved Instances (Save $3,200/mo)",
            "Downsize staging PostgreSQL instance from db.r6g.xlarge to db.r6g.large (Save $850/mo)",
            "Enable S3 Lifecycle Rules for backup snapshots older than 30 days (Save $420/mo)",
            "Utilize Redis memory compression for telemetry caches (Save $300/mo)",
        ]

        return {
            "id": str(uuid.uuid4()),
            "month_year": self._current_month,
            "provider": "MULTI_CLOUD",
            "total_cost_usd": total_cost,
            "monthly_budget_usd": budget,
            "budget_utilized_percent": utilized_percent,
            "service_breakdown": service_breakdown,
            "recommendations": recommendations,
            "budget_status": (
                "WITHIN_BUDGET" if utilized_percent < 85.0 else "WARNING_THRESHOLD"
            ),
            "generated_at": datetime.now(UTC).isoformat(),
        }

    def evaluate_budget_alert(
        self, current_spend: float, budget: float
    ) -> dict[str, Any]:
        """Evaluates whether cloud spend exceeds budget threshold."""
        percent = (current_spend / budget) * 100.0 if budget > 0 else 0.0
        return {
            "current_spend_usd": current_spend,
            "budget_usd": budget,
            "utilized_percent": round(percent, 1),
            "alert_triggered": percent >= 85.0,
            "severity": (
                "HIGH"
                if percent >= 95.0
                else ("MEDIUM" if percent >= 85.0 else "NORMAL")
            ),
        }
