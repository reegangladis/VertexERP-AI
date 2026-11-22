"""Structured JSON logging configuration and PII sanitization filters."""

import logging
import re
import sys
from collections.abc import MutableMapping
from typing import Any

import structlog

from app.core.config import settings
from app.core.context import get_correlation_id, get_tenant_id, get_user_id

# Sensitive keys to redact unconditionally from log records
SENSITIVE_KEYS = {
    "password",
    "password_hash",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "jwt_secret",
    "totp_secret",
    "api_key",
    "credit_card",
    "card_number",
    "ssn",
    "authorization",
    "private_key",
    "secret_key",
    "bearer",
    "cvv",
    "pan",
    "tax_identifier",
    "bank_account",
}

# Regex patterns for inline PII and secret redaction within string messages
_RE_JWT = re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}")
_RE_BEARER = re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.]+", re.IGNORECASE)
_RE_CREDIT_CARD = re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")
_RE_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_RE_API_KEY = re.compile(r"\b(?:sk|pk)_(?:live|test)_[a-zA-Z0-9]{24,}\b")


def sanitize_string_value(val: str) -> str:
    """Scans and redacts inline secrets, JWTs, and PII patterns from string log messages."""
    if not val or len(val) < 8:
        return val
    val = _RE_BEARER.sub("Bearer [REDACTED]", val)
    val = _RE_JWT.sub("[JWT_REDACTED]", val)
    val = _RE_CREDIT_CARD.sub("[CARD_REDACTED]", val)
    val = _RE_SSN.sub("[SSN_REDACTED]", val)
    val = _RE_API_KEY.sub("[APIKEY_REDACTED]", val)
    return val


def mask_sensitive_data(
    logger: Any, method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """Recursively redacts sensitive keys and patterns from log output."""
    for key, val in list(event_dict.items()):
        if isinstance(key, str) and any(s in key.lower() for s in SENSITIVE_KEYS):
            event_dict[key] = "[REDACTED]"
        elif isinstance(val, str):
            event_dict[key] = sanitize_string_value(val)
        elif isinstance(val, dict):
            event_dict[key] = dict(mask_sensitive_data(logger, method_name, val))
        elif isinstance(val, list):
            event_dict[key] = [
                sanitize_string_value(x)
                if isinstance(x, str)
                else (
                    dict(mask_sensitive_data(logger, method_name, x)) if isinstance(x, dict) else x
                )
                for x in val
            ]
    return event_dict


def inject_context_vars(
    logger: Any, method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """Injects correlation_id, tenant_id, user_id, environment from contextvars into log record."""
    corr_id = get_correlation_id()
    if corr_id and "correlation_id" not in event_dict:
        event_dict["correlation_id"] = corr_id

    tenant_id = get_tenant_id()
    if tenant_id and "tenant_id" not in event_dict:
        event_dict["tenant_id"] = str(tenant_id)

    user_id = get_user_id()
    if user_id and "user_id" not in event_dict:
        event_dict["user_id"] = str(user_id)

    if "environment" not in event_dict:
        event_dict["environment"] = settings.APP_ENV.value

    return event_dict


def setup_logging() -> None:
    """Configures global structured logging according to application settings."""
    log_level = getattr(logging, settings.LOG_LEVEL.value, logging.INFO)

    # Configure root standard library logger
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
        force=True,
    )

    # Disable noisy third-party loggers
    for noisy in ["uvicorn.access", "sqlalchemy.engine"]:
        logging.getLogger(noisy).setLevel(logging.WARNING)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        inject_context_vars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        mask_sensitive_data,
    ]

    if settings.LOG_JSON_FORMAT:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            renderer,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


# Module-level logger getter
logger = structlog.get_logger("vertexerp")
