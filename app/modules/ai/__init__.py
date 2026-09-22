"""VertexERP AI V2 Platform & Copilot Domain."""

from app.modules.ai.api.router import ai_router
from app.modules.ai.gateway.gateway import AIGateway, ai_gateway
from app.modules.ai.services.copilot_service import AICopilotService
from app.modules.ai.tools.registry import ERPToolRegistry, erp_tool_registry

__all__ = [
    "ai_router",
    "AIGateway",
    "ai_gateway",
    "AICopilotService",
    "ERPToolRegistry",
    "erp_tool_registry",
]
