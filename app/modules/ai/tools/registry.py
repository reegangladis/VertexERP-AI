"""Central Tool Registry for ERP Domain Tools."""

from __future__ import annotations

import logging
import time
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.ai.schemas.gateway import ToolDefinition
from app.modules.ai.security.tool_authorizer import ToolAuthorizer
from app.modules.ai.tools.base import BaseERPTool
from app.modules.ai.tools.erp_tools.finance_tools import (
    DraftVendorBillTool,
    GetFinancialKPISummaryTool,
    GetInvoiceSummaryTool,
)
from app.modules.ai.tools.erp_tools.hr_tools import GetDepartmentHeadcountTool
from app.modules.ai.tools.erp_tools.inventory_tools import (
    CheckProductStockTool,
    RequestStockTransferTool,
)
from app.modules.ai.tools.erp_tools.rag_tools import QueryKnowledgeBaseTool
from app.modules.ai.tools.erp_tools.sales_tools import (
    CreateDealOpportunityTool,
    GetOpenLeadsSummaryTool,
)

logger = logging.getLogger("vertexerp.ai.tools.registry")


class ERPToolRegistry:
    """Central registry of executable ERP domain tools."""

    def __init__(self):
        self._tools: dict[str, BaseERPTool] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Register default core ERP tools."""
        # Inventory
        self.register_tool(CheckProductStockTool())
        self.register_tool(RequestStockTransferTool())
        # Finance
        self.register_tool(GetInvoiceSummaryTool())
        self.register_tool(GetFinancialKPISummaryTool())
        self.register_tool(DraftVendorBillTool())
        # CRM / Sales
        self.register_tool(GetOpenLeadsSummaryTool())
        self.register_tool(CreateDealOpportunityTool())
        # HR
        self.register_tool(GetDepartmentHeadcountTool())
        # Knowledge Base / RAG
        self.register_tool(QueryKnowledgeBaseTool())

    def register_tool(self, tool: BaseERPTool) -> None:
        """Register a new tool instance."""
        self._tools[tool.name] = tool
        logger.debug(f"Registered AI ERP tool: {tool.name}")

    def get_tool(self, tool_name: str) -> BaseERPTool | None:
        """Retrieve tool instance by name."""
        return self._tools.get(tool_name)

    def get_all_tools(self) -> list[BaseERPTool]:
        """Return list of all registered tools."""
        return list(self._tools.values())

    def get_tool_definitions(self) -> list[ToolDefinition]:
        """Return all tool definitions formatted for LLM schema specification."""
        return [tool.to_tool_definition() for tool in self._tools.values()]

    async def execute_tool(
        self,
        tool_name: str,
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        user_permissions: set[str],
        is_superuser: bool = False,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Authorize and execute a tool within tenant boundaries."""
        tool = self.get_tool(tool_name)
        if not tool:
            raise NotFoundException(f"AI ERP tool '{tool_name}' not registered in platform.")

        # Zero-Trust authorization check
        ToolAuthorizer.authorize_tool(tool_name, user_permissions, is_superuser=is_superuser)

        start_time = time.perf_counter()
        params = parameters or {}

        try:
            result = await tool.execute(
                db=db,
                tenant_id=tenant_id,
                user_id=user_id,
                parameters=params,
            )
            execution_time_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                "success": True,
                "tool_name": tool_name,
                "result": result,
                "execution_time_ms": round(execution_time_ms, 2),
            }
        except Exception as exc:
            execution_time_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Error executing AI tool '{tool_name}': {str(exc)}", exc_info=True)
            return {
                "success": False,
                "tool_name": tool_name,
                "error": str(exc),
                "execution_time_ms": round(execution_time_ms, 2),
            }


# Singleton Tool Registry instance
erp_tool_registry = ERPToolRegistry()
