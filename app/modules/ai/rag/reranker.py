"""RAG Reranker for hybrid scoring (Vector Cosine + Lexical BM25 heuristic + Header boost)."""

from __future__ import annotations

import math
import re

from app.modules.ai.rag.retriever import RetrievedChunk
from app.modules.ai.schemas.rag import RAGSearchResultItem


class RAGReranker:
    """Hybrid ranker combining semantic vector similarity with lexical keyword overlap."""

    def __init__(
        self,
        vector_weight: float = 0.65,
        lexical_weight: float = 0.25,
        heading_weight: float = 0.10,
    ):
        self.vector_weight = vector_weight
        self.lexical_weight = lexical_weight
        self.heading_weight = heading_weight

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Tokenize text into lowercase alphanumeric words."""
        return re.findall(r"\b\w+\b", text.lower())

    def _compute_lexical_score(self, query_tokens: list[str], chunk_text: str) -> float:
        """Calculate lexical matching score based on term frequencies."""
        if not query_tokens or not chunk_text:
            return 0.0

        chunk_tokens = self._tokenize(chunk_text)
        if not chunk_tokens:
            return 0.0

        chunk_token_set = set(chunk_tokens)
        matched = sum(1 for q in query_tokens if q in chunk_token_set)
        token_coverage = matched / len(query_tokens)

        # Term frequency saturation
        tf_sum = sum(
            math.log(1.0 + chunk_tokens.count(q)) for q in query_tokens if q in chunk_token_set
        )
        tf_norm = min(1.0, tf_sum / (len(query_tokens) + 1.0))

        return round(0.6 * token_coverage + 0.4 * tf_norm, 4)

    def _compute_heading_boost(
        self, query_tokens: list[str], heading: str | None, title: str
    ) -> float:
        """Compute exact boost if query tokens match section heading or document title."""
        target = f"{title} {heading or ''}".lower()
        if not target.strip():
            return 0.0

        matched = sum(1 for q in query_tokens if q in target)
        return min(1.0, matched / max(1, len(query_tokens)))

    def rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> list[RAGSearchResultItem]:
        """Rerank candidates using hybrid scoring."""
        query_tokens = self._tokenize(query)
        scored_results: list[RAGSearchResultItem] = []

        for item in candidates:
            # Vector score normalized to [0, 1]
            vec_score = (
                max(0.0, min(1.0, (item.vector_score + 1.0) / 2.0))
                if item.vector_score < 0
                else item.vector_score
            )

            # Lexical term overlap
            lex_score = self._compute_lexical_score(query_tokens, item.content)

            # Heading / title exact match boost
            head_boost = self._compute_heading_boost(
                query_tokens, item.section_heading, item.document_title
            )

            # Composite weighted score
            composite = (
                self.vector_weight * vec_score
                + self.lexical_weight * lex_score
                + self.heading_weight * head_boost
            )
            composite = round(min(1.0, composite), 4)

            if composite >= min_score:
                scored_results.append(
                    RAGSearchResultItem(
                        chunk_id=item.chunk_id,
                        document_id=item.document_id,
                        document_title=item.document_title,
                        version_number=item.version_number,
                        chunk_index=item.chunk_index,
                        content=item.content,
                        section_heading=item.section_heading,
                        vector_score=round(vec_score, 4),
                        lexical_score=round(lex_score, 4),
                        composite_score=composite,
                        metadata=item.metadata,
                    )
                )

        # Sort by composite score descending
        scored_results.sort(key=lambda x: x.composite_score, reverse=True)
        return scored_results[:top_k]
