"""RAG Document Cleaner for text normalization and sanitization."""

from __future__ import annotations

import re
import unicodedata


class RAGCleaner:
    """Cleans and sanitizes raw document content before chunking and embedding."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Sanitize raw text for uniform vector embedding and indexing."""
        if not text:
            return ""

        # 1. Unicode normalization (NFKC)
        normalized = unicodedata.normalize("NFKC", text)

        # 2. Normalize line breaks (\r\n -> \n, \r -> \n)
        normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

        # 3. Strip null bytes and non-printable control characters (except newline, tab)
        normalized = "".join(
            ch for ch in normalized if ch in ("\n", "\t") or (ord(ch) >= 32 and ord(ch) != 127)
        )

        # 4. Remove HTML tags if present (e.g. <script>...</script> or <p>)
        normalized = re.sub(r"<script.*?</script>", "", normalized, flags=re.DOTALL | re.IGNORECASE)
        normalized = re.sub(r"<style.*?</style>", "", normalized, flags=re.DOTALL | re.IGNORECASE)
        normalized = re.sub(r"<[^>]+>", " ", normalized)

        # 5. Collapse multiple horizontal spaces and tabs into single space
        normalized = re.sub(r"[ \t]+", " ", normalized)

        # 6. Collapse 3+ consecutive newlines into double newline
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)

        return normalized.strip()
