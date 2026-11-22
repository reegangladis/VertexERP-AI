"""RAG Document Parser supporting text, markdown, json, csv formats."""

from __future__ import annotations

import csv
import io
import json
import logging
import re

logger = logging.getLogger("vertexerp.ai.rag.parser")


class ParsedSection:
    """A semantically identified section within a parsed document."""

    def __init__(self, heading: str | None, content: str, level: int = 1):
        self.heading = heading
        self.content = content
        self.level = level


class RAGParser:
    """Parser converting raw content strings and structured formats into parsed sections."""

    @staticmethod
    def parse_document(raw_content: str, file_type: str = "text") -> list[ParsedSection]:
        """Parse raw content into structured sections based on format."""
        file_type_norm = (file_type or "text").lower().strip()

        if file_type_norm in ("markdown", "md"):
            return RAGParser._parse_markdown(raw_content)
        elif file_type_norm in ("json", "application/json"):
            return RAGParser._parse_json(raw_content)
        elif file_type_norm in ("csv", "text/csv"):
            return RAGParser._parse_csv(raw_content)
        else:
            return RAGParser._parse_plain_text(raw_content)

    @staticmethod
    def _parse_markdown(content: str) -> list[ParsedSection]:
        """Parse markdown splitting by headers (#, ##, ###)."""
        lines = content.splitlines()
        sections: list[ParsedSection] = []
        current_heading: str | None = None
        current_lines: list[str] = []
        current_level: int = 1

        heading_pattern = re.compile(r"^(#{1,6})\s+(.*)$")

        for line in lines:
            match = heading_pattern.match(line.strip())
            if match:
                if current_lines:
                    text_block = "\n".join(current_lines).strip()
                    if text_block:
                        sections.append(
                            ParsedSection(
                                heading=current_heading,
                                content=text_block,
                                level=current_level,
                            )
                        )
                    current_lines = []

                hashes, heading_text = match.groups()
                current_heading = heading_text.strip()
                current_level = len(hashes)
            else:
                current_lines.append(line)

        if current_lines:
            text_block = "\n".join(current_lines).strip()
            if text_block:
                sections.append(
                    ParsedSection(
                        heading=current_heading,
                        content=text_block,
                        level=current_level,
                    )
                )

        if not sections:
            sections.append(ParsedSection(heading="Overview", content=content.strip(), level=1))

        return sections

    @staticmethod
    def _parse_json(content: str) -> list[ParsedSection]:
        """Parse JSON objects or arrays into human-readable textual representations."""
        try:
            data = json.loads(content)
        except Exception:
            # Fallback to plain text if invalid JSON
            return RAGParser._parse_plain_text(content)

        sections: list[ParsedSection] = []

        if isinstance(data, dict):
            for key, val in data.items():
                val_str = json.dumps(val, indent=2) if isinstance(val, (dict, list)) else str(val)
                sections.append(
                    ParsedSection(
                        heading=f"Section: {key}",
                        content=f"{key}:\n{val_str}",
                        level=2,
                    )
                )
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                val_str = (
                    json.dumps(item, indent=2) if isinstance(item, (dict, list)) else str(item)
                )
                sections.append(
                    ParsedSection(
                        heading=f"Item #{idx + 1}",
                        content=val_str,
                        level=2,
                    )
                )
        else:
            sections.append(ParsedSection(heading="Data", content=str(data), level=1))

        return sections

    @staticmethod
    def _parse_csv(content: str) -> list[ParsedSection]:
        """Parse CSV rows into declarative natural language rows."""
        sections: list[ParsedSection] = []
        try:
            reader = csv.DictReader(io.StringIO(content))
            rows = list(reader)
            if not rows:
                return RAGParser._parse_plain_text(content)

            # Group every 10 rows into a section
            chunk_size = 10
            for i in range(0, len(rows), chunk_size):
                batch = rows[i : i + chunk_size]
                lines: list[str] = []
                for r_idx, row in enumerate(batch):
                    fields = [f"{k}: {v}" for k, v in row.items() if v]
                    lines.append(f"Record {i + r_idx + 1}: " + " | ".join(fields))

                sections.append(
                    ParsedSection(
                        heading=f"Records {i + 1} to {min(i + chunk_size, len(rows))}",
                        content="\n".join(lines),
                        level=2,
                    )
                )
        except Exception:
            return RAGParser._parse_plain_text(content)

        return sections

    @staticmethod
    def _parse_plain_text(content: str) -> list[ParsedSection]:
        """Parse plain text documents by detecting double-newline paragraph breaks."""
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        if not paragraphs:
            return [ParsedSection(heading=None, content=content.strip(), level=1)]

        sections: list[ParsedSection] = []
        for idx, para in enumerate(paragraphs):
            # Check if first line looks like a title
            lines = para.splitlines()
            first_line = lines[0].strip()
            if len(first_line) < 80 and len(lines) > 1 and not first_line.endswith("."):
                heading = first_line
                body = "\n".join(lines[1:]).strip()
            else:
                heading = f"Section {idx + 1}"
                body = para

            sections.append(ParsedSection(heading=heading, content=body, level=1))

        return sections
