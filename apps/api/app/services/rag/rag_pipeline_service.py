import uuid
from typing import Any
from app.services.rag.retrieval_service import RAGRetrievalService


class RAGPipelineService:
    def __init__(self, retrieval_service: RAGRetrievalService):
        self.retrieval_service = retrieval_service

    async def answer_query(
        self,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        query: str,
        session_id: uuid.UUID | None = None,
        chat_history: list[dict[str, str]] | None = None,
        collection_ids: list[uuid.UUID] | None = None,
        provider: str = "openai",
        model_name: str = "gpt-4o",
        temperature: float = 0.7,
        top_k: int = 5,
        search_type: str = "hybrid"
    ) -> dict[str, Any]:
        """
        Processes query, retrieves isolated context, builds prompts with citations,
        and coordinates with the pluggable LLM provider for response generation.
        """
        # Step 1: Retrieve context chunks
        retrieval_response = await self.retrieval_service.retrieve(
            org_id=org_id,
            user_id=user_id,
            query=query,
            collection_ids=collection_ids,
            top_k=top_k,
            search_type=search_type,
            provider=provider
        )

        retrieved_chunks = retrieval_response["results"]

        # Step 2: Context Assembly
        context_blocks = []
        citations = []

        for i, chunk in enumerate(retrieved_chunks):
            ref_id = f"[{i + 1}]"
            context_blocks.append(
                f"Source {ref_id} - Title: {chunk['document_title']}\n"
                f"Content: {chunk['content']}"
            )
            citations.append({
                "document_id": chunk["document_id"],
                "document_title": chunk["document_title"],
                "chunk_id": chunk["chunk_id"],
                "chunk_index": chunk["chunk_index"],
                "snippet": chunk["content"][:200] + "...",
                "score": chunk["score"]
            })

        context_str = "\n\n".join(context_blocks) if context_blocks else "No reference documents found."

        # Step 3: Prompt Construction
        system_prompt = (
            "You are an enterprise AI assistant for VertexERP AI. Answer the user query using only "
            "the provided source documents. If you don't know or the content is not present in "
            "the context, state that clearly. Cite the documents you use in your response with [1], [2], etc."
        )

        history_str = ""
        if chat_history:
            history_str = "\nConversation History:\n"
            for msg in chat_history[-6:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_str += f"{role.capitalize()}: {content}\n"

        full_prompt = (
            f"{system_prompt}\n"
            f"{history_str}\n"
            f"Context:\n{context_str}\n\n"
            f"User Query: {query}\n"
            f"Answer:"
        )

        # Step 4: LLM Abstraction Layer Response Generation
        response_text = self._mock_llm_response(query, retrieved_chunks, provider, model_name)

        prompt_tokens = int(len(full_prompt) / 4)
        completion_tokens = int(len(response_text) / 4)

        return {
            "answer": response_text,
            "citations": citations,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "retrieved_chunks": retrieved_chunks
        }

    def _mock_llm_response(self, query: str, chunks: list[dict], provider: str, model_name: str) -> str:
        if not chunks:
            return "I couldn't find any relevant document snippets in the VertexERP AI database to answer your question."

        best_chunk = chunks[0]
        title = best_chunk["document_title"]
        snippet = best_chunk["content"]

        return (
            f"Based on the enterprise document '{title}' [1], the relevant details suggest: "
            f"'{snippet[:120]}...'. This response was generated using model '{model_name}' "
            f"hosted via provider '{provider}'."
        )
