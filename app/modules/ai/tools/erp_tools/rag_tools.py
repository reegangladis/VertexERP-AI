"""RAG knowledge base tool for AI Copilot."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.rag.rag_service import rag_service
from app.modules.ai.schemas.rag import RAGSearchRequest
from app.modules.ai.tools.base import BaseERPTool

logger = logging.getLogger("vertexerp.ai.tools.rag")


class QueryKnowledgeBaseTool(BaseERPTool):
    """Tool allowing AI Copilot to query company documentation, SOPs, policies, and manuals."""

    @property
    def name(self) -> str:
        return "query_knowledge_base"

    @property
    def description(self) -> str:
        return (
            "Search and retrieve company SOPs, organizational policies, manufacturing guidelines, "
            "product manuals, and documentation from the knowledge base using semantic vector search."
        )

    @property
    def is_mutation(self) -> bool:
        return False

    @property
    def action_type(self) -> str:
        return "knowledge.query"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query to find relevant documents and SOPs.",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of top relevant sections to retrieve (default: 3).",
                    "default": 3,
                },
            },
            "required": ["query"],
        }

    def preview(self, parameters: dict[str, Any]) -> str:
        query = parameters.get("query", "")
        return f"Search knowledge base for documentation matching: '{query}'"

    async def execute(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        organization_id: UUID,
        parameters: dict[str, Any],
        user_id: UUID | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute knowledge search."""
        query = parameters.get("query", "").strip()
        top_k = parameters.get("top_k", 3)

        if not query:
            return {"error": "Search query cannot be empty."}

        search_req = RAGSearchRequest(
            query=query,
            top_k=top_k,
            min_score=0.0,
        )

        user_roles = set(context.get("user_roles", [])) if context else {"StandardUser"}
        user_dept = context.get("user_department") if context else None

        resp = await rag_service.search_knowledge(
            session=session,
            tenant_id=tenant_id,
            payload=search_req,
            user_roles=user_roles,
            user_department=user_dept,
        )

        results_data = []
        for item in resp.results:
            results_data.append(
                {
                    "document_title": item.document_title,
                    "version": item.version_number,
                    "chunk_index": item.chunk_index,
                    "section_heading": item.section_heading,
                    "content": item.content,
                    "relevance_score": item.composite_score,
                }
            )

        return {
            "query": query,
            "total_matches": len(results_data),
            "results": results_data,
        }
