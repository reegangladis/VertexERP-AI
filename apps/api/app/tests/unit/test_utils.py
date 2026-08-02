import uuid
from datetime import UTC, timedelta

import pytest

from app.core.exceptions import ValidationException
from app.utils.date import days_between, format_iso, parse_iso, utc_now
from app.utils.pagination import get_pagination_metadata
from app.utils.uuid import is_valid_uuid, new_uuid, to_uuid
from app.utils.validation import (
    validate_email,
    validate_required,
    validate_string_length,
)


def test_date_utilities():
    """Verify standard date utilities return correct timestamps and calculations."""
    now = utc_now()
    assert now.tzinfo == UTC

    # ISO formatting & parsing
    formatted = format_iso(now)
    parsed = parse_iso(formatted)
    assert abs((now - parsed).total_seconds()) < 1.0

    # Days between
    yesterday = now - timedelta(days=1)
    assert days_between(now, yesterday) == 1


def test_uuid_utilities():
    """Verify uuid tools identify and format correct identifiers."""
    generated = new_uuid()
    assert isinstance(generated, uuid.UUID)
    assert is_valid_uuid(generated) is True
    assert is_valid_uuid(str(generated)) is True
    assert is_valid_uuid("not-a-uuid") is False

    converted = to_uuid(str(generated))
    assert converted == generated


def test_pagination_helper():
    """Verify pagination metadata calculations."""
    meta = get_pagination_metadata(total_count=25, skip=10, limit=5)
    assert meta["total_count"] == 25
    assert meta["limit"] == 5
    assert meta["skip"] == 10
    assert meta["page"] == 3
    assert meta["total_pages"] == 5
    assert meta["has_next"] is True
    assert meta["has_previous"] is True

    # Check boundaries
    meta_boundary = get_pagination_metadata(total_count=3, skip=0, limit=10)
    assert meta_boundary["total_pages"] == 1
    assert meta_boundary["has_next"] is False
    assert meta_boundary["has_previous"] is False


def test_validation_helpers():
    """Verify validation helpers successfully flag anomalies and validate clean arguments."""
    # Required
    validate_required("some text", "field")
    with pytest.raises(ValidationException):
        validate_required(None, "field")
    with pytest.raises(ValidationException):
        validate_required("", "field")
    with pytest.raises(ValidationException):
        validate_required("  ", "field")

    # String length
    validate_string_length("hello", 2, 10, "field")
    with pytest.raises(ValidationException):
        validate_string_length("h", 2, 10, "field")
    with pytest.raises(ValidationException):
        validate_string_length("hello world", 2, 10, "field")

    # Email format
    validate_email("test@example.com")
    with pytest.raises(ValidationException):
        validate_email("invalid-email")
