import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """Hashes a clear text password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a clear text password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def hash_token(raw_token: str) -> str:
    """Hashes a raw token string using SHA-256 for secure DB storage."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_access_token(
    subject: str | Any, expires_delta: timedelta | None = None
) -> str:
    """Generates a short-lived access JWT token."""
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject), "type": "access", "jti": uuid.uuid4().hex}
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(
    subject: str | Any, expires_delta: timedelta | None = None
) -> str:
    """Generates a long-lived refresh JWT token."""
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh", "jti": uuid.uuid4().hex}
    return jwt.encode(
        to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str, is_refresh: bool = False) -> str | None:
    """Decodes a JWT token and returns the subject if valid."""
    secret = settings.JWT_REFRESH_SECRET_KEY if is_refresh else settings.JWT_SECRET_KEY
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def validate_password_strength(password: str) -> list[str]:
    """Validates password strength against enterprise policies."""
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter.")
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter.")
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit.")
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character.")
    return errors


def generate_totp_secret() -> str:
    """Generates a random base32 TOTP secret."""
    import base64
    import secrets
    random_bytes = secrets.token_bytes(20)
    return base64.b32encode(random_bytes).decode("utf-8").replace("=", "")


def verify_totp_code(secret: str, code: str) -> bool:
    """Verifies a 6-digit TOTP code against a secret for current & adjacent time windows."""
    import base64
    import hmac
    import struct
    import time

    if not secret or not code or len(code) != 6 or not code.isdigit():
        return False

    try:
        # Add padding if needed
        missing_padding = len(secret) % 8
        if missing_padding:
            secret += "=" * (8 - missing_padding)
        key = base64.b32decode(secret, casefold=True)
    except Exception:
        return False

    current_time = int(time.time())
    # Check current window and adjacent windows (-1, 0, +1)
    for offset in (-1, 0, 1):
        time_step = (current_time // 30) + offset
        msg = struct.pack(">Q", time_step)
        h = hmac.new(key, msg, "sha1").digest()
        offset_val = h[-1] & 0x0F
        binary = struct.unpack(">I", h[offset_val:offset_val + 4])[0] & 0x7FFFFFFF
        otp = binary % 1000000
        if f"{otp:06d}" == code:
            return True
    return False

