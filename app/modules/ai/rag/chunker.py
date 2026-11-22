"""RAG Chunker for semantic and sliding-window chunking."""

from __future__ import annotations

from typing import Any

from app.modules.ai.rag.cleaner import RAGCleaner
from app.modules.ai.rag.parser import RAGParser


class ChunkItem:
    """Represents an atomic text chunk ready for vector embedding and indexing."""

    def __init__(
        self,
        chunk_index: int,
        content: str,
        token_count: int,
        char_count: int,
        section_heading: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.chunk_index = chunk_index
        self.content = content
        self.token_count = token_count
        self.char_count = char_count
        self.section_heading = section_heading
        self.metadata = metadata or {}


class RAGChunker:
    """Semantic and sliding window chunker with section preservation and token counting."""

    def __init__(
        self,
        chunk_size_tokens: int = 400,
        chunk_overlap_tokens: int = 50,
        approx_chars_per_token: float = 4.0,
    ):
        self.chunk_size_tokens = chunk_size_tokens
        self.chunk_overlap_tokens = chunk_overlap_tokens
        self.approx_chars_per_token = approx_chars_per_token

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count based on whitespace tokens and character heuristic."""
        if not text:
            return 0
        words = text.split()
        char_est = int(len(text) / self.approx_chars_per_token)
        # Combine word count and character count heuristic
        return max(1, max(len(words), char_est))

    def chunk_document(
        self,
        raw_content: str,
        file_type: str = "text",
        doc_metadata: dict[str, Any] | None = None,
    ) -> list[ChunkItem]:
        """Parse, clean, and chunk document into indexed ChunkItems."""
        doc_meta = doc_metadata or {}
        parsed_sections = RAGParser.parse_document(raw_content, file_type=file_type)

        chunks: list[ChunkItem] = []
        global_index = 0

        for section in parsed_sections:
            cleaned_content = RAGCleaner.clean_text(section.content)
            if not cleaned_content:
                continue

            section_tokens = self.estimate_tokens(cleaned_content)

            # If section fits within chunk size, keep it whole
            if section_tokens <= self.chunk_size_tokens:
                header_prefix = f"[{section.heading}]\n" if section.heading else ""
                full_text = f"{header_prefix}{cleaned_content}".strip()

                chunk = ChunkItem(
                    chunk_index=global_index,
                    content=full_text,
                    token_count=self.estimate_tokens(full_text),
                    char_count=len(full_text),
                    section_heading=section.heading,
                    metadata={
                        **doc_meta,
                        "section_heading": section.heading,
                        "section_level": section.level,
                    },
                )
                chunks.append(chunk)
                global_index += 1
            else:
                # Section exceeds chunk size -> perform sliding window chunking
                sub_chunks = self._sliding_window_chunk(
                    cleaned_content,
                    section_heading=section.heading,
                    start_index=global_index,
                    doc_metadata=doc_meta,
                )
                chunks.extend(sub_chunks)
                global_index += len(sub_chunks)

        return chunks

    def _sliding_window_chunk(
        self,
        text: str,
        section_heading: str | None,
        start_index: int,
        doc_metadata: dict[str, Any],
    ) -> list[ChunkItem]:
        """Split large text into overlapping windows of words."""
        words = text.split()
        sub_chunks: list[ChunkItem] = []
        curr_idx = start_index

        # Convert token parameters to approximate word parameters
        words_per_chunk = max(20, int(self.chunk_size_tokens * 0.75))
        words_overlap = max(5, int(self.chunk_overlap_tokens * 0.75))
        step = max(1, words_per_chunk - words_overlap)

        header_prefix = f"[{section_heading}]\n" if section_heading else ""

        for i in range(0, len(words), step):
            chunk_words = words[i : i + words_per_chunk]
            if not chunk_words:
                break

            body = " ".join(chunk_words)
            full_text = f"{header_prefix}{body}".strip()

            chunk = ChunkItem(
                chunk_index=curr_idx,
                content=full_text,
                token_count=self.estimate_tokens(full_text),
                char_count=len(full_text),
                section_heading=section_heading,
                metadata={
                    **doc_metadata,
                    "section_heading": section_heading,
                    "sub_chunk_offset": i,
                },
            )
            sub_chunks.append(chunk)
            curr_idx += 1

            if i + words_per_chunk >= len(words):
                break

        return sub_chunks
