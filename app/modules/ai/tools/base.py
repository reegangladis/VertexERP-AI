"""Base class for ERP domain tools executable by AI Copilot."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.schemas.gateway import FunctionDefinition, ToolDefinition


class BaseERPTool(ABC):
    """Abstract base class for all ERP AI tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier of the tool (e.g. 'check_product_stock')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Clear description provided to the LLM indicating when and how to invoke this tool."""
        pass

    @property
    @abstractmethod
    def parameters_schema(self) -> dict[str, Any]:
        """JSON Schema defining required and optional parameters."""
        pass

    @property
    def is_mutation(self) -> bool:
        """Indicates if this tool mutates data and requires human confirmation."""
        return False

    @property
    def action_type(self) -> str:
        """Category/action classification (e.g. 'inventory.query', 'finance.bill.create')."""
        return "general.query"

    def to_tool_definition(self) -> ToolDefinition:
        """Convert into standard OpenAI/LLM tool definition format."""
        return ToolDefinition(
            type="function",
            function=FunctionDefinition(
                name=self.name,
                description=self.description,
                parameters=self.parameters_schema,
            ),
        )

    def preview(self, parameters: dict[str, Any]) -> str:
        """Generate human-readable summary of the proposed action for user confirmation."""
        return f"Execute {self.name} with parameters: {parameters}"

    @abstractmethod
    async def execute(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute the business logic with tenant isolation. Returns JSON-serializable dict."""
        pass
