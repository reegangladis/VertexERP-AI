"""Unit tests for Argon2id hashing and password validation."""

from app.core.security import (
    generate_secure_token,
    hash_password,
    validate_password_strength,
    verify_password,
)


def test_argon2id_hash_and_verify():
    """Verifies Argon2id password hashing and positive/negative verification."""
    password = "StrongPassword123!@#"
    hashed = hash_password(password)

    assert hashed.startswith("$argon2id$")
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123!@#", hashed) is False


def test_generate_secure_token():
    """Verifies generation of high-entropy URL-safe random tokens."""
    token1 = generate_secure_token(32)
    token2 = generate_secure_token(32)
    assert len(token1) >= 40
    assert token1 != token2


def test_validate_password_strength():
    """Verifies password strength policy rules."""
    assert validate_password_strength("short") == "Password must be at least 12 characters long."
    assert (
        validate_password_strength("alllowercase123!")
        == "Password must contain at least one uppercase letter."
    )
    assert (
        validate_password_strength("ALLUPPERCASE123!")
        == "Password must contain at least one lowercase letter."
    )
    assert (
        validate_password_strength("NoNumbersAtAll!!")
        == "Password must contain at least one number."
    )
    assert (
        validate_password_strength("NoSpecialChar123")
        == "Password must contain at least one special character."
    )
    assert validate_password_strength("ValidStrongPassword123!") is None
