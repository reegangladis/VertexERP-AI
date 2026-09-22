"""Dedicated worker for asynchronous heavy ERP report generation."""

import csv
import io
import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.jobs.models.job import BackgroundJob
from app.modules.jobs.workers.base import BaseWorker

logger = logging.getLogger("vertexerp.jobs.reports")


class ReportsWorker(BaseWorker):
    """Worker responsible for compiling and generating heavy ERP analytical reports."""

    job_type: str = "reports"

    async def process(
        self,
        job: BackgroundJob,
        payload: dict[str, Any],
        session: AsyncSession,
    ) -> dict[str, Any]:
        """
        Generate asynchronous business reports (GL Balance Sheet, Inventory Valuation, Sales Analytics).
        """
        report_type = payload.get("report_type", "general_summary")
        report_format = payload.get("format", "json").lower()
        payload.get("filters", {})

        if payload.get("simulate_error") and (job.retry_count + 1) < payload.get(
            "fail_until_attempt", payload.get("fail_until_retry", 999)
        ):
            raise TimeoutError(
                "Simulated heavy database aggregation timeout during report generation"
            )

        rows: list[dict[str, Any]] = []
        summary: dict[str, Any] = {}

        if report_type == "balance_sheet":
            rows = [
                {
                    "account_code": "1000",
                    "account_name": "Operating Cash & Bank",
                    "type": "ASSET",
                    "balance": 450000.00,
                },
                {
                    "account_code": "1200",
                    "account_name": "Accounts Receivable",
                    "type": "ASSET",
                    "balance": 185000.00,
                },
                {
                    "account_code": "1400",
                    "account_name": "Merchandise Inventory",
                    "type": "ASSET",
                    "balance": 320000.00,
                },
                {
                    "account_code": "2000",
                    "account_name": "Accounts Payable",
                    "type": "LIABILITY",
                    "balance": 140000.00,
                },
                {
                    "account_code": "3000",
                    "account_name": "Retained Earnings",
                    "type": "EQUITY",
                    "balance": 815000.00,
                },
            ]
            summary = {
                "total_assets": 955000.00,
                "total_liabilities": 140000.00,
                "total_equity": 815000.00,
            }

        elif report_type == "inventory_valuation":
            rows = [
                {
                    "sku": "SKU-STEEL-01",
                    "name": "Cold Rolled Steel Sheet",
                    "quantity": 1200,
                    "unit_cost": 45.0,
                    "total_value": 54000.0,
                },
                {
                    "sku": "SKU-ALUM-02",
                    "name": "Aluminum Bar 6061",
                    "quantity": 800,
                    "unit_cost": 28.5,
                    "total_value": 22800.0,
                },
                {
                    "sku": "SKU-COPPER-03",
                    "name": "Copper Wire Spool",
                    "quantity": 450,
                    "unit_cost": 110.0,
                    "total_value": 49500.0,
                },
            ]
            summary = {
                "total_skus": len(rows),
                "total_inventory_value": sum(r["total_value"] for r in rows),
            }

        elif report_type == "sales_summary":
            rows = [
                {
                    "region": "North America",
                    "orders_count": 145,
                    "gross_revenue": 580000.00,
                    "margin_pct": 34.2,
                },
                {
                    "region": "EMEA",
                    "orders_count": 98,
                    "gross_revenue": 395000.00,
                    "margin_pct": 31.8,
                },
                {
                    "region": "APAC",
                    "orders_count": 112,
                    "gross_revenue": 440000.00,
                    "margin_pct": 36.5,
                },
            ]
            summary = {
                "total_orders": sum(r["orders_count"] for r in rows),
                "total_revenue": sum(r["gross_revenue"] for r in rows),
            }

        else:
            rows = [
                {"metric": "Active Users", "value": 42},
                {"metric": "Transactions Today", "value": 1890},
            ]
            summary = {"generated_items": len(rows)}

        # Format output
        artifact_id = f"rpt_{uuid.uuid4().hex[:12]}"
        file_content: str = ""
        if report_format == "csv":
            output = io.StringIO()
            if rows:
                writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
            file_content = output.getvalue()
        else:
            file_content = json.dumps({"summary": summary, "data": rows}, indent=2)

        logger.info(
            "Generated report '%s' in format '%s' for tenant %s (%d rows)",
            report_type,
            report_format,
            job.tenant_id,
            len(rows),
        )

        return {
            "report_type": report_type,
            "format": report_format,
            "artifact_id": artifact_id,
            "row_count": len(rows),
            "summary": summary,
            "sample_data": rows[:5],
            "file_size_bytes": len(file_content.encode("utf-8")),
            "download_url": f"/api/v1/jobs/reports/download/{artifact_id}",
            "generated_at": datetime.now(UTC).isoformat(),
        }
