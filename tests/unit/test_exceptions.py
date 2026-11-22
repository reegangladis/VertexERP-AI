"""Unit tests for domain exception hierarchy."""

from app.core.exceptions import (
    ConflictException,
    DatabaseConnectionException,
    ForbiddenException,
    NotFoundException,
    RedisConnectionException,
    UnauthorizedException,
    ValidationException,
)


def test_exception_status_codes_and_defaults():
    """Verifies that domain exceptions define proper HTTP status codes and RFC 7807 metadata."""
    not_found = NotFoundException("Item missing")
    assert not_found.status_code == 404
    assert not_found.title == "Resource Not Found"
    assert not_found.detail == "Item missing"

    conflict = ConflictException("Duplicate SKU")
    assert conflict.status_code == 409

    val_err = ValidationException("Invalid email format")
    assert val_err.status_code == 422

    unauth = UnauthorizedException("Token expired")
    assert unauth.status_code == 401

    forbidden = ForbiddenException("Missing permission")
    assert forbidden.status_code == 403

    db_err = DatabaseConnectionException("Database down")
    assert db_err.status_code == 503

    redis_err = RedisConnectionException("Redis down")
    assert redis_err.status_code == 503


def test_exception_with_invalid_params():
    """Verifies that invalid parameter lists are stored in exception instance."""
    params = [{"field": "amount", "reason": "Must be > 0"}]
    exc = ValidationException("Validation failed", invalid_params=params)
    assert exc.invalid_params == params
