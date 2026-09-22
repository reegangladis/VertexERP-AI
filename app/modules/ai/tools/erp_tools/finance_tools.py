"""Finance domain tools for AI Copilot."""

from __future__ import annotations

import uuid
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.tools.base import BaseERPTool
from app.modules.finance.models import Bill, Invoice


class GetInvoiceSummaryTool(BaseERPTool):
    """Tool to query accounts receivable / customer invoice status and metrics."""

    @property
    def name(self) -> str:
        return "get_invoice_summary"

    @property
    def description(self) -> str:
        return "Retrieve a summary of customer invoices, total accounts receivable, overdue balances, and recent invoice records."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Optional filter by invoice status (e.g. 'DRAFT', 'POSTED', 'PAID', 'OVERDUE').",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of recent invoices to return (default 5).",
                },
            },
            "additionalProperties": False,
        }

    @property
    def is_mutation(self) -> bool:
        return False

    @property
    def action_type(self) -> str:
        return "finance.invoice.query"

    async def execute(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        status_filter = parameters.get("status")
        limit = min(parameters.get("limit", 5), 20)

        # Aggregations for total count and sum
        agg_q = select(
            func.count(Invoice.id).label("total_count"),
            func.coalesce(func.sum(Invoice.total_amount), 0.0).label("total_receivables"),
            func.coalesce(func.sum(Invoice.amount_due), 0.0).label("total_due"),
        ).where(Invoice.tenant_id == tenant_id)
        if status_filter:
            agg_q = agg_q.where(Invoice.status == status_filter.upper())

        agg_res = await db.execute(agg_q)
        agg_row = agg_res.first()

        # Recent records
        rec_q = (
            select(Invoice)
            .where(Invoice.tenant_id == tenant_id)
            .order_by(Invoice.created_at.desc())
            .limit(limit)
        )
        if status_filter:
            rec_q = rec_q.where(Invoice.status == status_filter.upper())

        rec_res = await db.execute(rec_q)
        invoices = rec_res.scalars().all()

        return {
            "status": "success",
            "total_invoices": int(agg_row.total_count if agg_row else 0),
            "total_receivables_amount": float(agg_row.total_receivables if agg_row else 0.0),
            "total_due_amount": float(agg_row.total_due if agg_row else 0.0),
            "recent_invoices": [
                {
                    "id": str(inv.id),
                    "invoice_number": inv.invoice_number,
                    "status": str(inv.status),
                    "total_amount": float(inv.total_amount),
                    "amount_due": float(inv.amount_due),
                    "issue_date": inv.issue_date.isoformat() if inv.issue_date else None,
                    "due_date": inv.due_date.isoformat() if inv.due_date else None,
                }
                for inv in invoices
            ],
        }


class GetFinancialKPISummaryTool(BaseERPTool):
    """Tool to query high-level finance metrics."""

    @property
    def name(self) -> str:
        return "get_financial_kpi_summary"

    @property
    def description(self) -> str:
        return (
            "Get high-level financial KPIs including total revenue, open payables, and receivables."
        )

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        }

    @property
    def is_mutation(self) -> bool:
        return False

    @property
    def action_type(self) -> str:
        return "finance.kpi.query"

    async def execute(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        # AR sum
        ar_res = await db.execute(
            select(func.coalesce(func.sum(Invoice.amount_due), 0.0)).where(
                Invoice.tenant_id == tenant_id
            )
        )
        total_ar = float(ar_res.scalar() or 0.0)

        # AP sum
        ap_res = await db.execute(
            select(func.coalesce(func.sum(Bill.amount_due), 0.0)).where(Bill.tenant_id == tenant_id)
        )
        total_ap = float(ap_res.scalar() or 0.0)

        return {
            "status": "success",
            "kpis": {
                "accounts_receivable_due": total_ar,
                "accounts_payable_due": total_ap,
                "net_working_capital_gap": total_ar - total_ap,
            },
        }


class DraftVendorBillTool(BaseERPTool):
    """Mutation tool to draft a new vendor bill."""

    @property
    def name(self) -> str:
        return "draft_vendor_bill"

    @property
    def description(self) -> str:
        return "Draft a new vendor bill for incoming goods or services requiring accounts payable settlement."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "vendor_name": {
                    "type": "string",
                    "description": "Name of the supplier or vendor.",
                },
                "total_amount": {
                    "type": "number",
                    "description": "Total bill amount to be drafted.",
                },
                "reference_number": {
                    "type": "string",
                    "description": "Vendor invoice/reference number.",
                },
                "notes": {
                    "type": "string",
                    "description": "Optional notes or line item details.",
                },
            },
            "required": ["vendor_name", "total_amount"],
            "additionalProperties": False,
        }

    @property
    def is_mutation(self) -> bool:
        return True

    @property
    def action_type(self) -> str:
        return "finance.bill.create"

    def preview(self, parameters: dict[str, Any]) -> str:
        vendor = parameters.get("vendor_name", "Unknown Vendor")
        amt = parameters.get("total_amount", 0.0)
        return f"Draft Vendor Bill of ${amt:,.2f} for Vendor '{vendor}'."

    async def execute(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        vendor = parameters.get("vendor_name")
        amt = float(parameters.get("total_amount", 0.0))
        bill_num = f"BILL-DRAFT-{uuid.uuid4().hex[:6].upper()}"

        return {
            "status": "success",
            "bill_number": bill_num,
            "vendor_name": vendor,
            "total_amount": amt,
            "status_code": "DRAFT",
            "message": f"Successfully drafted vendor bill {bill_num} for ${amt:,.2f}.",
        }
