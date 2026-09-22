"""Human Resources domain tools for AI Copilot."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.tools.base import BaseERPTool
from app.modules.hr.models import Employee


class GetDepartmentHeadcountTool(BaseERPTool):
    """Tool to query organization headcount and active staff distribution."""

    @property
    def name(self) -> str:
        return "get_department_headcount"

    @property
    def description(self) -> str:
        return "Get employee headcount statistics, total active staff, and department breakdown."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "department_id": {
                    "type": "string",
                    "description": "Optional department UUID to filter.",
                }
            },
            "additionalProperties": False,
        }

    @property
    def is_mutation(self) -> bool:
        return False

    @property
    def action_type(self) -> str:
        return "hr.headcount.query"

    async def execute(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        # Count total active employees
        tot_q = (
            select(func.count(Employee.id))
            .where(Employee.tenant_id == tenant_id)
            .where(Employee.is_active.is_(True))
        )
        tot_res = await db.execute(tot_q)
        total_active = tot_res.scalar() or 0

        # Group by department if department_id present
        dept_q = (
            select(Employee.department_id, func.count(Employee.id))
            .where(Employee.tenant_id == tenant_id)
            .where(Employee.is_active.is_(True))
            .group_by(Employee.department_id)
        )
        dept_res = await db.execute(dept_q)
        dept_counts = [
            {"department_id": str(d_id) if d_id else "Unassigned", "headcount": count}
            for d_id, count in dept_res.all()
        ]

        return {
            "status": "success",
            "total_active_headcount": int(total_active),
            "department_breakdown": dept_counts,
        }
