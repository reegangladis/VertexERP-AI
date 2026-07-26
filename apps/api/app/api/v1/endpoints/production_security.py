import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.repositories.production_repository import ProductionRepository
from app.services.security_hardening import SecurityHardeningService
from app.models.production import SecurityAuditLog
from app.schemas.production import SecurityAuditLogOut

router = APIRouter()
sec_service = SecurityHardeningService()


@router.get("/audits", response_model=List[SecurityAuditLogOut])
async def list_security_audit_logs(
    severity: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List security audit logs and OWASP violation detections."""
    repo = ProductionRepository(db)
    return await repo.list_security_audit_logs(severity=severity)


@router.post("/sanitize-check")
async def test_input_sanitization(input_text: str = Query(...)):
    """Tests XSS input sanitization and SQL injection detection."""
    sanitized = sec_service.sanitize_input(input_text)
    is_sqli = sec_service.detect_sqli(input_text)
    return {
        "raw_input": input_text,
        "sanitized_output": sanitized,
        "sqli_detected": is_sqli,
    }


@router.post("/rotate-secret")
async def rotate_system_secret(secret_name: str = Query("JWT_SECRET_KEY")):
    """Triggers secret rotation for enterprise security keys."""
    return sec_service.rotate_secret(secret_name)


@router.get("/secret-rotation-status")
async def get_secret_rotation_status():
    """Returns key rotation health and due dates."""
    return sec_service.get_secret_rotation_status()
