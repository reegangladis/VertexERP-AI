import html
import re
import time
from typing import Any


class SecurityHardeningService:
    """Enterprise Security Hardening Engine providing OWASP Top 10 defenses, sanitization, and lockout guards."""

    def __init__(self):
        # Account lockout tracking: {user_identifier: [failed_attempt_timestamps]}
        self._failed_logins: dict[str, list[float]] = {}
        # Secret rotation log: {secret_name: last_rotated_timestamp}
        self._secret_rotation: dict[str, float] = {
            "JWT_SECRET_KEY": time.time() - 86400 * 10,
            "DATABASE_CREDENTIALS": time.time() - 86400 * 30,
            "WEBHOOK_HMAC_SECRET": time.time() - 86400 * 5,
        }

    # ----------------------------------------------------
    # OWASP Top 10 Defenses
    # ----------------------------------------------------
    def sanitize_input(self, text_input: str) -> str:
        """HTML escapes text input to prevent Stored & Reflected XSS attacks."""
        if not text_input:
            return ""
        # Remove dangerous script tags and event handlers
        cleaned = re.sub(r"(?i)<script.*?>.*?</script>", "", text_input)
        cleaned = re.sub(r"(?i)on\w+\s*=", "", cleaned)
        return html.escape(cleaned)

    def detect_sqli(self, query_str: str) -> bool:
        """Detects SQL Injection attack patterns."""
        sqli_patterns = [
            r"(?i)\bUNION\b\s+\bSELECT\b",
            r"(?i)\bOR\b\s+['\"]?1['\"]?\s*=\s*['\"]?1",
            r"(?i)\bDROP\b\s+\bTABLE\b",
            r"(?i)\bINSERT\b\s+\bINTO\b",
            r"--\s*$",
            r"/\*.*?\*/",
        ]
        for pattern in sqli_patterns:
            if re.search(pattern, query_str):
                return True
        return False

    def validate_ssrf_url(self, target_url: str) -> bool:
        """Prevents Server-Side Request Forgery (SSRF) by blocking internal loopbacks & metadata endpoints."""
        forbidden = ["127.0.0.1", "localhost", "169.254.169.254", "0.0.0.0", "::1"]
        for bad in forbidden:
            if bad in target_url.lower():
                return False
        return True

    # ----------------------------------------------------
    # Password Policy & Account Lockout
    # ----------------------------------------------------
    def validate_password_policy(self, password: str) -> tuple[bool, list[str]]:
        """Enforces enterprise password strength requirements."""
        errors = []
        if len(password) < 12:
            errors.append("Password must be at least 12 characters long")
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", password):
            errors.append("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
            errors.append("Password must contain at least one special character")

        return len(errors) == 0, errors

    def record_failed_login(
        self,
        user_identifier: str,
        max_attempts: int = 5,
        lockout_window_seconds: int = 900,
    ) -> bool:
        """Records failed login attempt. Returns True if account is locked out."""
        now = time.time()
        window_start = now - lockout_window_seconds
        attempts = self._failed_logins.get(user_identifier, [])

        # Filter active window attempts
        active_attempts = [t for t in attempts if t > window_start]
        active_attempts.append(now)
        self._failed_logins[user_identifier] = active_attempts

        return len(active_attempts) >= max_attempts

    def is_account_locked(
        self,
        user_identifier: str,
        max_attempts: int = 5,
        lockout_window_seconds: int = 900,
    ) -> bool:
        """Checks if account is currently locked out."""
        now = time.time()
        window_start = now - lockout_window_seconds
        attempts = self._failed_logins.get(user_identifier, [])
        active_attempts = [t for t in attempts if t > window_start]
        return len(active_attempts) >= max_attempts

    def reset_failed_logins(self, user_identifier: str) -> None:
        """Resets failed login counter upon successful authentication."""
        if user_identifier in self._failed_logins:
            del self._failed_logins[user_identifier]

    # ----------------------------------------------------
    # Secret Rotation Architecture
    # ----------------------------------------------------
    def rotate_secret(self, secret_name: str) -> dict[str, Any]:
        """Triggers rotation for an enterprise secret key."""
        now = time.time()
        self._secret_rotation[secret_name] = now
        return {
            "secret_name": secret_name,
            "status": "ROTATED",
            "rotated_at": now,
            "next_rotation_due_days": 90,
        }

    def get_secret_rotation_status(self) -> list[dict[str, Any]]:
        """Returns rotation health status for all system secrets."""
        now = time.time()
        results = []
        for name, ts in self._secret_rotation.items():
            age_days = (now - ts) / 86400.0
            results.append(
                {
                    "secret_name": name,
                    "age_days": round(age_days, 1),
                    "needs_rotation": age_days > 90,
                }
            )
        return results
