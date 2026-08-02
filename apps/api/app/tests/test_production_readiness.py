import pytest

from app.services.backup_recovery_service import BackupRecoveryService
from app.services.compliance_service import ComplianceService
from app.services.resilience_engine import (
    Bulkhead,
    CircuitBreaker,
    CircuitBreakerOpenException,
    ResilienceEngine,
)
from app.services.security_hardening import SecurityHardeningService


# 1. Security Hardening Tests
def test_input_sanitization_xss():
    sec = SecurityHardeningService()
    raw_xss = (
        '<script>alert("XSS")</script><img src="x" onerror="javascript:alert(1)"/>'
    )
    sanitized = sec.sanitize_input(raw_xss)

    assert "<script>" not in sanitized
    assert "onerror=" not in sanitized
    assert "&lt;" in sanitized or sanitized == ""


def test_sqli_detection():
    sec = SecurityHardeningService()
    sqli_attack = "SELECT * FROM users WHERE username = 'admin' OR '1'='1'"
    clean_input = "john.doe@company.com"

    assert sec.detect_sqli(sqli_attack) is True
    assert sec.detect_sqli(clean_input) is False


def test_ssrf_url_validation():
    sec = SecurityHardeningService()
    assert sec.validate_ssrf_url("https://api.partner.com/v1") is True
    assert sec.validate_ssrf_url("http://127.0.0.1/admin") is False
    assert sec.validate_ssrf_url("http://169.254.169.254/latest/meta-data") is False


def test_password_policy_validation():
    sec = SecurityHardeningService()
    valid, errors = sec.validate_password_policy("V3rtexERP#2026!Secure")
    assert valid is True
    assert len(errors) == 0

    invalid, errors = sec.validate_password_policy("weak")
    assert invalid is False
    assert len(errors) > 0


def test_account_lockout():
    sec = SecurityHardeningService()
    user = "locked_user_test"

    for _ in range(4):
        locked = sec.record_failed_login(user, max_attempts=5)
        assert locked is False

    # 5th attempt triggers lockout
    locked = sec.record_failed_login(user, max_attempts=5)
    assert locked is True
    assert sec.is_account_locked(user, max_attempts=5) is True

    sec.reset_failed_logins(user)
    assert sec.is_account_locked(user, max_attempts=5) is False


def test_secret_rotation():
    sec = SecurityHardeningService()
    res = sec.rotate_secret("JWT_SECRET_KEY")
    assert res["status"] == "ROTATED"

    status_list = sec.get_secret_rotation_status()
    assert len(status_list) >= 3


# 2. Resilience Engine Tests
def test_circuit_breaker_transitions():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=0.5)

    def failing_func():
        raise RuntimeError("Service failure")

    # 1st failure
    with pytest.raises(RuntimeError):
        cb.call(failing_func)
    assert cb.state == "CLOSED"

    # 2nd failure opens circuit
    with pytest.raises(RuntimeError):
        cb.call(failing_func)
    assert cb.state == "OPEN"

    # Subsequent call while OPEN is rejected immediately
    with pytest.raises(CircuitBreakerOpenException):
        cb.call(lambda: "ok")


def test_bulkhead_concurrency_limit():
    bulkhead = Bulkhead(max_concurrent_calls=2)

    with bulkhead:
        with bulkhead:
            # 3rd concurrent call exceeds capacity
            with pytest.raises(RuntimeError):
                with bulkhead:
                    pass


def test_retry_with_jitter_and_fallback():
    engine = ResilienceEngine()
    calls = []

    def primary():
        calls.append("tried")
        if len(calls) < 2:
            raise ValueError("Transient error")
        return "success"

    res = engine.execute_retry_with_jitter(primary, max_retries=3, base_delay=0.01)
    assert res == "success"
    assert len(calls) == 2

    # Fallback test
    fallback_res = engine.execute_with_fallback(lambda: 1 / 0, lambda: "fallback_value")
    assert fallback_res == "fallback_value"


# 3. Backup & Disaster Recovery Tests
def test_backup_trigger_and_checksum():
    svc = BackupRecoveryService()
    backup = svc.trigger_backup("test_prod_snapshot", "FULL")
    assert backup["status"] == "COMPLETED"

    verification = svc.verify_backup_integrity(backup["id"])
    assert verification["valid"] is True
    assert verification["checksum_verified"] is True


def test_disaster_recovery_restore_simulation():
    svc = BackupRecoveryService()
    backup = svc.trigger_backup("test_dr_snapshot")
    restore = svc.simulate_disaster_recovery_restore(
        backup["id"], "disaster_recovery_standby"
    )

    assert restore["status"] == "VERIFIED"
    assert restore["rpo_target_met"] is True
    assert restore["rto_target_met"] is True


# 4. Compliance Engine Tests
def test_compliance_evaluation_and_gdpr():
    svc = ComplianceService()
    soc2 = svc.evaluate_compliance_framework("SOC2")
    assert soc2["overall_score"] >= 90.0
    assert soc2["framework"] == "SOC2"

    gdpr_res = svc.process_gdpr_forget_request("user_forget@example.com")
    assert gdpr_res["status"] == "COMPLETED"
    assert "anonymized_" in gdpr_res["anonymized_identifier"]
