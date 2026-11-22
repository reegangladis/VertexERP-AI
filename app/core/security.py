"""Security primitives: Argon2id hashing, RFC 6238 TOTP, and JWT token utilities."""

import base64
import hashlib
import hmac
import json
import os
import secrets
import struct
import time
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings

# Argon2id hasher with OWASP-recommended parameters
_ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,  # 64 MiB
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    """Hashes a plaintext password using Argon2id."""
    return _ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against an Argon2id hash."""
    try:
        return _ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, Exception):
        return False


def needs_rehash(hashed_password: str) -> bool:
    """Checks if password hash needs updating to newer algorithm parameters."""
    return _ph.check_needs_rehash(hashed_password)


def generate_secure_token(num_bytes: int = 32) -> str:
    """Generates a high-entropy URL-safe cryptographic token."""
    return secrets.token_urlsafe(num_bytes)


def hash_token(token: str) -> str:
    """Computes a SHA-256 hash of an opaque token for safe database indexing."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def validate_password_strength(password: str) -> str | None:
    """Validates enterprise password strength policy."""
    if len(password) < 12:
        return "Password must be at least 12 characters long."
    if not any(c.isupper() for c in password):
        return "Password must contain at least one uppercase letter."
    if not any(c.islower() for c in password):
        return "Password must contain at least one lowercase letter."
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one number."
    if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password):
        return "Password must contain at least one special character."
    return None


# ------------------------------------------------------------------------------
# RFC 6238 TOTP Engine (Two-Factor Authentication)
# ------------------------------------------------------------------------------
def generate_totp_secret() -> str:
    """Generates a random 160-bit Base32-encoded TOTP shared secret."""
    random_bytes = secrets.token_bytes(20)
    return base64.b32encode(random_bytes).decode("utf-8").replace("=", "")


def compute_totp_code(secret_b32: str, for_time: int | None = None, interval: int = 30) -> str:
    """Computes the 6-digit RFC 6238 TOTP code for a given timestamp."""
    if for_time is None:
        for_time = int(time.time())

    # Pad Base32 string to multiple of 8
    missing_padding = len(secret_b32) % 8
    if missing_padding != 0:
        secret_b32 += "=" * (8 - missing_padding)

    key = base64.b32decode(secret_b32, casefold=True)
    time_counter = struct.pack(">Q", for_time // interval)
    h = hmac.new(key, time_counter, hashlib.sha1).digest()

    offset = h[-1] & 0x0F
    code_int = struct.unpack(">I", h[offset : offset + 4])[0] & 0x7FFFFFFF
    code_str = str(code_int % 1000000).zfill(6)
    return code_str


def verify_totp_code(secret_b32: str, code: str, allowed_drift_steps: int = 1) -> bool:
    """Verifies a 6-digit TOTP code allowing for clock drift."""
    if not code or len(code) != 6 or not code.isdigit():
        return False

    current_time = int(time.time())
    for step in range(-allowed_drift_steps, allowed_drift_steps + 1):
        test_time = current_time + (step * 30)
        expected_code = compute_totp_code(secret_b32, for_time=test_time)
        if secrets.compare_digest(expected_code, code):
            return True
    return False


def encrypt_secret(plain_text: str, key_material: str | None = None) -> str:
    """Encrypts sensitive data (e.g. TOTP secret) using AES-256-GCM."""
    key = hashlib.sha256((key_material or settings.JWT_SECRET_KEY).encode("utf-8")).digest()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plain_text.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_secret(encrypted_text: str, key_material: str | None = None) -> str:
    """Decrypts AES-256-GCM encrypted data."""
    key = hashlib.sha256((key_material or settings.JWT_SECRET_KEY).encode("utf-8")).digest()
    data = base64.b64decode(encrypted_text.encode("utf-8"))
    nonce, ciphertext = data[:12], data[12:]
    aesgcm = AESGCM(key)
    decrypted = aesgcm.decrypt(nonce, ciphertext, None)
    return decrypted.decode("utf-8")


# ------------------------------------------------------------------------------
# JWT Token Encoding & Decoding (HMAC-SHA256 / RS256 standard)
# ------------------------------------------------------------------------------
def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("utf-8"))


def create_jwt_token(
    payload: dict[str, Any],
    expires_delta: timedelta,
    secret_key: str | None = None,
) -> str:
    """Creates a signed JWT token with standard claims."""
    now = datetime.now(UTC)
    to_encode = payload.copy()
    to_encode.update(
        {
            "iat": int(now.timestamp()),
            "exp": int((now + expires_delta).timestamp()),
            "iss": "https://auth.vertexerp.io",
            "jti": to_encode.get("jti", str(uuid.uuid4())),
        }
    )

    header = {"typ": "JWT", "alg": "HS256"}
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(to_encode, separators=(",", ":")).encode("utf-8"))

    signing_input = f"{header_b64}.{payload_b64}".encode()
    secret = (secret_key or settings.JWT_SECRET_KEY).encode("utf-8")
    signature = hmac.new(secret, signing_input, hashlib.sha256).digest()
    signature_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_jwt_token(
    token: str,
    secret_key: str | None = None,
) -> dict[str, Any]:
    """Decodes and cryptographically verifies a JWT token. Raises ValueError on invalid/expired."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Malformed JWT token structure.")

        header_b64, payload_b64, signature_b64 = parts

        # Cryptographic Header Algorithm Enforcement (Anti-Algorithm Confusion)
        header: dict[str, Any] = json.loads(_b64url_decode(header_b64).decode("utf-8"))
        if header.get("alg") != "HS256" or header.get("typ") != "JWT":
            raise ValueError(f"Unsupported or invalid JWT algorithm '{header.get('alg')}'.")

        signing_input = f"{header_b64}.{payload_b64}".encode()
        secret = (secret_key or settings.JWT_SECRET_KEY).encode("utf-8")
        expected_sig = hmac.new(secret, signing_input, hashlib.sha256).digest()
        provided_sig = _b64url_decode(signature_b64)

        if not hmac.compare_digest(expected_sig, provided_sig):
            raise ValueError("Invalid cryptographic token signature.")

        payload: dict[str, Any] = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        exp = payload.get("exp")
        if exp is not None and int(exp) < int(datetime.now(UTC).timestamp()):
            raise ValueError("Token has expired.")

        return payload
    except Exception as exc:
        raise ValueError(f"JWT verification failed: {exc}") from exc
