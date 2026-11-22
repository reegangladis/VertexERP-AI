"""MFA service for TOTP enrollment, encryption, and verification."""

import secrets

from app.core.security import (
    decrypt_secret,
    encrypt_secret,
    generate_totp_secret,
    hash_password,
    verify_password,
    verify_totp_code,
)


class MfaService:
    """Service managing RFC 6238 TOTP enrollment, secret encryption, and verification."""

    @staticmethod
    def setup_mfa(
        user_email: str, issuer: str = "VertexERP"
    ) -> tuple[str, str, str, list[str], list[str]]:
        """
        Initializes TOTP setup:
        - Generates Base32 secret
        - Generates AES-GCM encrypted secret for database storage
        - Generates otpauth:// URI for QR code rendering
        - Generates 8 single-use recovery codes
        """
        secret = generate_totp_secret()
        encrypted_secret = encrypt_secret(secret)
        otpauth_url = f"otpauth://totp/{issuer}:{user_email}?secret={secret}&issuer={issuer}&algorithm=SHA1&digits=6&period=30"

        # Generate 8 recovery codes
        plain_recovery_codes = [secrets.token_hex(5).upper() for _ in range(8)]
        hashed_recovery_codes = [hash_password(code) for code in plain_recovery_codes]

        return secret, encrypted_secret, otpauth_url, plain_recovery_codes, hashed_recovery_codes

    @staticmethod
    def verify_code(encrypted_secret: str, code: str) -> bool:
        """Decrypts TOTP secret and validates 6-digit code."""
        secret = decrypt_secret(encrypted_secret)
        return verify_totp_code(secret, code)

    @staticmethod
    async def verify_code_with_replay_prevention(
        encrypted_secret: str,
        code: str,
        user_id: object | None = None,
        redis: object | None = None,
    ) -> bool:
        """Decrypts TOTP secret, validates 6-digit code, and prevents token replay attacks."""
        secret = decrypt_secret(encrypted_secret)
        is_valid = verify_totp_code(secret, code)
        if not is_valid:
            return False

        if redis is not None and user_id is not None:
            cache_key = f"mfa:consumed:{user_id}:{code}"
            already_used = await redis.get(cache_key)
            if already_used:
                return False
            await redis.set(cache_key, "1", ex=90)

        return True

    @staticmethod
    def verify_recovery_code(
        hashed_recovery_codes: list[str], plain_code: str
    ) -> tuple[bool, list[str]]:
        """Verifies recovery code and burns the consumed code."""
        for idx, hashed in enumerate(hashed_recovery_codes):
            if verify_password(plain_code.strip().upper(), hashed):
                # Consume code
                updated_codes = hashed_recovery_codes[:idx] + hashed_recovery_codes[idx + 1 :]
                return True, updated_codes
        return False, hashed_recovery_codes
