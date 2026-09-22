"""Zero-Trust Security Guardrails: Prompt Injection Detection & Sensitive Data Redaction."""

from __future__ import annotations

import re
from typing import NamedTuple

from app.core.metrics import metrics_registry


class GuardrailCheckResult(NamedTuple):
    is_safe: bool
    reason: str | None
    sanitized_prompt: str


# Regex patterns matching prompt injection and jailbreak techniques
PROMPT_INJECTION_PATTERNS: list[tuple[str, re.Pattern]] = [
    (
        "System prompt override attempt",
        re.compile(
            r"(ignore\s+(all\s+)?(previous|prior|above)\s+instructions|disregard\s+(all\s+)?(previous|prior)\s+instructions|system\s+prompt\s+override)",
            re.IGNORECASE,
        ),
    ),
    (
        "Jailbreak / Roleplay escape",
        re.compile(
            r"(you\s+are\s+now\s+in\s+DAN\s+mode|do\s+anything\s+now|developer\s+mode\s+enabled|pretend\s+to\s+have\s+no\s+rules)",
            re.IGNORECASE,
        ),
    ),
    (
        "Direct SQL injection probe",
        re.compile(
            r"(\bUNION\s+SELECT\b|\bDROP\s+TABLE\b|\bDELETE\s+FROM\b|;\s*SELECT\s+.*\s+FROM\b)",
            re.IGNORECASE,
        ),
    ),
    (
        "System credential exfiltration attempt",
        re.compile(
            r"(reveal|print|display|dump|leak)\s+(your\s+)?(system\s+prompt|master\s+key|jwt\s+secret|database\s+password|api\s+key)",
            re.IGNORECASE,
        ),
    ),
]

# Sensitive data redaction patterns (PII, tokens, keys)
REDACTION_PATTERNS: list[tuple[str, re.Pattern, str]] = [
    (
        "Credit Card",
        re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
        "[REDACTED_CREDIT_CARD]",
    ),
    (
        "Social Security / National ID",
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "[REDACTED_SSN]",
    ),
    (
        "Bearer / JWT Token",
        re.compile(r"Bearer\s+eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+"),
        "Bearer [REDACTED_JWT]",
    ),
    (
        "API Key (Generic)",
        re.compile(
            r"(api[_-]?key|secret[_-]?key)\s*[:=]\s*['\"][A-Za-z0-9-_]{20,}['\"]", re.IGNORECASE
        ),
        r"\1: '[REDACTED_SECRET]'",
    ),
]


class AIGuardrails:
    """Security Guardrails analyzer for AI inputs and outputs."""

    @staticmethod
    def inspect_input(prompt: str) -> GuardrailCheckResult:
        """Analyze user prompt for prompt injections, system prompt leak attempts, or harmful content.

        Returns GuardrailCheckResult.
        """
        if not prompt or not prompt.strip():
            return GuardrailCheckResult(is_safe=True, reason=None, sanitized_prompt="")

        # 1. Check for prompt injection attempts
        for rule_name, pattern in PROMPT_INJECTION_PATTERNS:
            if pattern.search(prompt):
                metrics_registry.ai_guardrail_blocks_total.inc(labels={"violation_type": rule_name})
                return GuardrailCheckResult(
                    is_safe=False,
                    reason=f"Security violation detected: {rule_name}",
                    sanitized_prompt=prompt,
                )

        # 2. Redact sensitive PII and secrets before sending downstream
        sanitized = AIGuardrails.redact_sensitive_data(prompt)

        return GuardrailCheckResult(
            is_safe=True,
            reason=None,
            sanitized_prompt=sanitized,
        )

    @staticmethod
    def redact_sensitive_data(text: str) -> str:
        """Redact sensitive PII, passwords, and tokens from text."""
        if not text:
            return ""

        result = text
        for _, pattern, replacement in REDACTION_PATTERNS:
            result = pattern.sub(replacement, result)

        return result
