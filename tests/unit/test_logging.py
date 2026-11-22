"""Unit tests for structured logging and PII masking filter."""

import uuid

from app.core.context import set_correlation_id, set_tenant_id, set_user_id
from app.core.logging import inject_context_vars, mask_sensitive_data


def test_pii_masking_filter():
    """Verifies that sensitive keys are replaced with [REDACTED]."""
    event_dict = {
        "event": "user_login",
        "email": "user@example.com",
        "password": "SuperSecretPassword123!",
        "access_token": "eyJhbGciOi...",
        "nested": {
            "credit_card": "4111222233334444",
            "safe_field": "visible",
        },
    }
    masked = mask_sensitive_data(None, "info", event_dict)

    assert masked["password"] == "[REDACTED]"
    assert masked["access_token"] == "[REDACTED]"
    assert masked["nested"]["credit_card"] == "[REDACTED]"
    assert masked["nested"]["safe_field"] == "visible"
    assert masked["email"] == "user@example.com"


def test_context_vars_injection():
    """Verifies that active contextvars are automatically appended to log event dictionary."""
    corr_id = "req_test_12345"
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()

    set_correlation_id(corr_id)
    set_tenant_id(tenant_id)
    set_user_id(user_id)

    event_dict = {"event": "test_event"}
    injected = inject_context_vars(None, "info", event_dict)

    assert injected["correlation_id"] == corr_id
    assert injected["tenant_id"] == str(tenant_id)
    assert injected["user_id"] == str(user_id)
