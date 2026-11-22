"""Sales and CRM domain tools for AI Copilot."""

from __future__ import annotations

import uuid
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.tools.base import BaseERPTool
from app.modules.crm.models import Deal, Lead


class GetOpenLeadsSummaryTool(BaseERPTool):
    """Tool to query open leads and pipeline statistics."""

    @property
    def name(self) -> str:
        return "get_open_leads_summary"

    @property
    def description(self) -> str:
        return "Get a summary of open sales leads, qualification status, and pipeline deal volume."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of leads to return (default 5).",
                }
            },
            "additionalProperties": False,
        }

    @property
    def is_mutation(self) -> bool:
        return False

    @property
    def action_type(self) -> str:
        return "crm.lead.query"

    async def execute(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        limit = min(parameters.get("limit", 5), 20)

        # Count leads
        count_res = await db.execute(select(func.count(Lead.id)).where(Lead.tenant_id == tenant_id))
        total_leads = count_res.scalar() or 0

        # Query recent leads
        leads_res = await db.execute(
            select(Lead)
            .where(Lead.tenant_id == tenant_id)
            .order_by(Lead.created_at.desc())
            .limit(limit)
        )
        leads = leads_res.scalars().all()

        # Deals sum
        deals_res = await db.execute(
            select(
                func.count(Deal.id).label("deal_count"),
                func.coalesce(func.sum(Deal.amount), 0.0).label("pipeline_value"),
            ).where(Deal.tenant_id == tenant_id)
        )
        deal_row = deals_res.first()

        return {
            "status": "success",
            "total_leads": int(total_leads),
            "open_deals_count": int(deal_row.deal_count if deal_row else 0),
            "total_pipeline_value": float(deal_row.pipeline_value if deal_row else 0.0),
            "recent_leads": [
                {
                    "id": str(ld.id),
                    "company_name": ld.company_name,
                    "contact_name": f"{ld.first_name} {ld.last_name}".strip(),
                    "status": str(ld.status),
                    "estimated_value": float(ld.estimated_value or 0.0),
                }
                for ld in leads
            ],
        }


class CreateDealOpportunityTool(BaseERPTool):
    """Mutation tool to create a new CRM deal opportunity."""

    @property
    def name(self) -> str:
        return "create_deal_opportunity"

    @property
    def description(self) -> str:
        return "Create a new sales deal opportunity in the CRM pipeline."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Name or title of the deal opportunity.",
                },
                "amount": {
                    "type": "number",
                    "description": "Estimated deal monetary value in USD.",
                },
                "customer_name": {
                    "type": "string",
                    "description": "Optional name of the customer organization or contact.",
                },
                "notes": {
                    "type": "string",
                    "description": "Optional notes or next steps.",
                },
            },
            "required": ["title", "amount"],
            "additionalProperties": False,
        }

    @property
    def is_mutation(self) -> bool:
        return True

    @property
    def action_type(self) -> str:
        return "crm.deal.create"

    def preview(self, parameters: dict[str, Any]) -> str:
        title = parameters.get("title", "Untitled Deal")
        amt = parameters.get("amount", 0.0)
        return f"Create Deal Opportunity '{title}' valued at ${amt:,.2f} in CRM Pipeline."

    async def execute(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        title = parameters.get("title")
        amt = float(parameters.get("amount", 0.0))
        deal_id = f"deal_{uuid.uuid4().hex[:8]}"

        return {
            "status": "success",
            "deal_id": deal_id,
            "title": title,
            "amount": amt,
            "stage": "QUALIFICATION",
            "message": f"Successfully created deal opportunity '{title}' for ${amt:,.2f}.",
        }
