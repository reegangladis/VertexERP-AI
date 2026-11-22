"""Zero-Trust Tool Authorization Engine."""

from __future__ import annotations

import logging

from app.core.exceptions import ForbiddenException
from app.core.permissions import PermissionCode

logger = logging.getLogger("vertexerp.ai.security.tool_authorizer")

# Mapping of AI tool names to required ERP business permission codes
TOOL_PERMISSION_MAP: dict[str, list[str]] = {
    # Read tools (automatic if authorized)
    "check_product_stock": [
        PermissionCode.INVENTORY_PRODUCTS_READ.value,
        PermissionCode.INVENTORY_WAREHOUSES_READ.value,
        "inventory.read",
        "inventory:products:read",
    ],
    "get_invoice_summary": [
        PermissionCode.FINANCE_INVOICES_READ.value,
        "finance.read",
        "finance:invoices:read",
    ],
    "get_department_headcount": [
        PermissionCode.HR_EMPLOYEES_READ.value,
        "hr.read",
        "hr:employees:read",
    ],
    "get_financial_kpi_summary": [
        PermissionCode.FINANCE_ACCOUNTS_READ.value,
        PermissionCode.ANALYTICS_FINANCE_READ.value,
        "finance.read",
        "analytics.read",
    ],
    "get_open_leads_summary": [
        PermissionCode.CRM_LEADS_READ.value,
        PermissionCode.CRM_DEALS_READ.value,
        "crm.read",
    ],
    "query_knowledge_base": [
        PermissionCode.AI_RAG_QUERY.value,
        PermissionCode.AI_RAG_DOCUMENTS_READ.value,
        PermissionCode.AI_COPILOT_USE.value,
        "ai.rag.query",
        "ai:rag:query",
        "ai:copilot:use",
    ],
    # Mutation tools (require confirmation + write permission)
    "create_deal_opportunity": [
        PermissionCode.CRM_DEALS_WRITE.value,
        "crm.write",
        "crm:deals:write",
    ],
    "draft_vendor_bill": [
        PermissionCode.FINANCE_BILLS_WRITE.value,
        "finance.write",
        "finance:bills:write",
    ],
    "request_stock_transfer": [
        PermissionCode.INVENTORY_TRANSFERS_WRITE.value,
        "inventory.write",
        "inventory:transfers:write",
    ],
}


class ToolAuthorizer:
    """Validates that the authenticated user possesses explicit permission to invoke a given AI tool."""

    @staticmethod
    def authorize_tool(
        tool_name: str,
        user_permissions: set[str],
        is_superuser: bool = False,
    ) -> bool:
        """Check if user has permission to execute the specified tool.

        Raises ForbiddenException if unauthorized.
        """
        if is_superuser:
            return True

        # Check general AI tool execution permission
        ai_exec_perm = PermissionCode.AI_TOOLS_EXECUTE.value
        if (
            ai_exec_perm not in user_permissions
            and "ai:all" not in user_permissions
            and "*" not in user_permissions
        ):
            logger.warning(f"User denied tool execution: missing base permission {ai_exec_perm}")
            raise ForbiddenException(
                f"User does not have permission to execute AI tools ({ai_exec_perm})"
            )

        required_perms = TOOL_PERMISSION_MAP.get(tool_name)
        if not required_perms:
            return True

        # Check if user has ANY of the acceptable permission codes for this tool
        has_perm = (
            any(p in user_permissions for p in required_perms)
            or "*" in user_permissions
            or "admin" in user_permissions
        )
        if not has_perm:
            logger.warning(
                f"User denied tool execution '{tool_name}': missing required permission from {required_perms}"
            )
            raise ForbiddenException(
                f"User lacks required permissions for tool '{tool_name}'. Required: {required_perms[0]}"
            )

        return True

    @staticmethod
    def is_mutation_tool(tool_name: str) -> bool:
        """Return True if tool performs database mutations and requires user confirmation."""
        mutation_tools = {
            "create_deal_opportunity",
            "draft_vendor_bill",
            "request_stock_transfer",
            "cancel_purchase_order",
            "update_employee_salary",
        }
        return (
            tool_name in mutation_tools
            or tool_name.startswith("create_")
            or tool_name.startswith("draft_")
            or tool_name.startswith("delete_")
            or tool_name.startswith("update_")
        )
