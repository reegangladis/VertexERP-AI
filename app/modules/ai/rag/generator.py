"""RAG Generator synthesizing grounded answers with structured in-line citations."""

from __future__ import annotations

import logging
import re
import time

from app.modules.ai.gateway.gateway import ai_gateway
from app.modules.ai.schemas.gateway import ChatCompletionRequest, ChatMessage, MessageRole
from app.modules.ai.schemas.rag import RAGQueryCitation, RAGQueryResponse, RAGSearchResultItem

logger = logging.getLogger("vertexerp.ai.rag.generator")


class RAGGenerator:
    """Generates grounded responses from retrieved context chunks and extracts verifiable citations."""

    SYSTEM_PROMPT = """You are the VertexERP AI Knowledge & Compliance Assistant.
Your task is to answer the user's question accurately and objectively using ONLY the retrieved document context below.

CRITICAL GROUNDING RULES:
1. Ground every claim directly in the provided context chunks.
2. If the context does NOT contain enough information to answer the question, state: "Based on the available documentation, I do not have enough verified information to answer this question." Do not fabricate or speculate.
3. IN-LINE CITATIONS: For every factual statement, append an explicit citation tag in the exact format:
   [Doc: <document_title>, v<version_number>, Chunk: <chunk_index>]
4. Keep the answer professional, concise, structured, and easy to read.

--- RETRIEVED KNOWLEDGE BASE CONTEXT ---
{context_blocks}
----------------------------------------"""

    @staticmethod
    def _format_context_blocks(chunks: list[RAGSearchResultItem]) -> str:
        """Format chunks into distinct referenced blocks."""
        blocks: list[str] = []
        for c in chunks:
            heading_info = f" (Section: {c.section_heading})" if c.section_heading else ""
            block = (
                f"### [Doc: {c.document_title}, v{c.version_number}, Chunk: {c.chunk_index}]{heading_info}\n"
                f"{c.content}"
            )
            blocks.append(block)
        return "\n\n".join(blocks)

    @staticmethod
    def _extract_citations(
        answer_text: str, chunks: list[RAGSearchResultItem]
    ) -> list[RAGQueryCitation]:
        """Extract citations referenced in the text and match against source chunks."""
        # Citation regex pattern: [Doc: <title>, v<version>, Chunk: <index>]
        citation_pattern = re.compile(r"\[Doc:\s*(.*?),\s*v(\d+),\s*Chunk:\s*(\d+)\]")
        matches = citation_pattern.findall(answer_text)

        citations_dict: dict[tuple[str, int, int], RAGQueryCitation] = {}

        # First pass: direct citation pattern matches in text
        for _title, ver_str, chunk_str in matches:
            v_num = int(ver_str)
            c_idx = int(chunk_str)
            matching_chunk = next(
                (c for c in chunks if c.chunk_index == c_idx and c.version_number == v_num),
                None,
            )
            if matching_chunk:
                key = (
                    matching_chunk.document_title,
                    matching_chunk.version_number,
                    matching_chunk.chunk_index,
                )
                if key not in citations_dict:
                    snippet = matching_chunk.content[:200] + (
                        "..." if len(matching_chunk.content) > 200 else ""
                    )
                    citations_dict[key] = RAGQueryCitation(
                        document_id=matching_chunk.document_id,
                        document_title=matching_chunk.document_title,
                        version_number=matching_chunk.version_number,
                        chunk_index=matching_chunk.chunk_index,
                        section_heading=matching_chunk.section_heading,
                        snippet=snippet,
                        relevance_score=matching_chunk.composite_score,
                    )

        # Fallback: if model did not produce strict inline tags or referenced top chunk, include the top chunk citation
        if not citations_dict and chunks:
            top_chunk = chunks[0]
            snippet = top_chunk.content[:200] + ("..." if len(top_chunk.content) > 200 else "")
            citations_dict[
                (top_chunk.document_title, top_chunk.version_number, top_chunk.chunk_index)
            ] = RAGQueryCitation(
                document_id=top_chunk.document_id,
                document_title=top_chunk.document_title,
                version_number=top_chunk.version_number,
                chunk_index=top_chunk.chunk_index,
                section_heading=top_chunk.section_heading,
                snippet=snippet,
                relevance_score=top_chunk.composite_score,
            )

        return list(citations_dict.values())

    async def generate_grounded_answer(
        self,
        query: str,
        ranked_chunks: list[RAGSearchResultItem],
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
    ) -> RAGQueryResponse:
        """Generate answer grounded in retrieved chunks and return response with citations."""
        start_time = time.perf_counter()

        if not ranked_chunks:
            return RAGQueryResponse(
                query=query,
                answer="No relevant documentation was found in the knowledge base to answer your question.",
                citations=[],
                retrieved_chunks_count=0,
                provider_used=provider or "mock",
                model_used=model or "mock-gpt-4o",
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd=0.0,
                latency_ms=round((time.perf_counter() - start_time) * 1000.0, 2),
            )

        context_blocks = self._format_context_blocks(ranked_chunks)
        system_content = self.SYSTEM_PROMPT.format(context_blocks=context_blocks)

        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=system_content),
            ChatMessage(role=MessageRole.USER, content=query),
        ]

        chat_request = ChatCompletionRequest(
            messages=messages,
            provider=provider,
            model=model,
            temperature=temperature,
        )

        resp = await ai_gateway.chat_completion(chat_request)
        answer_text = resp.choices[0].message.content or ""

        # Extract structured citations
        citations = self._extract_citations(answer_text, ranked_chunks)
        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return RAGQueryResponse(
            query=query,
            answer=answer_text,
            citations=citations,
            retrieved_chunks_count=len(ranked_chunks),
            provider_used=resp.provider,
            model_used=resp.model,
            prompt_tokens=resp.usage.prompt_tokens,
            completion_tokens=resp.usage.completion_tokens,
            total_tokens=resp.usage.total_tokens,
            cost_usd=resp.cost_usd,
            latency_ms=latency_ms,
        )
