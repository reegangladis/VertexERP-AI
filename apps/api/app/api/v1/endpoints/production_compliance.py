from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.models.production import ComplianceReport
from app.repositories.production_repository import ProductionRepository
from app.schemas.production import (
    ComplianceReportOut,
    GDPRDataDeletionRequest,
)
from app.services.compliance_service import ComplianceService

router = APIRouter()
comp_service = ComplianceService()


@router.post(
    "/evaluate", response_model=ComplianceReportOut, status_code=status.HTTP_201_CREATED
)
async def evaluate_compliance_framework(
    framework: str = Query("SOC2", description="SOC2, ISO27001, GDPR, HIPAA"),
    db: AsyncSession = Depends(get_db),
):
    """Triggers automated compliance audit evaluation for a target framework."""
    repo = ProductionRepository(db)
    eval_res = comp_service.evaluate_compliance_framework(framework)

    report = ComplianceReport(
        framework=eval_res["framework"],
        overall_score=eval_res["overall_score"],
        passed_controls=eval_res["passed_controls"],
        failed_controls=eval_res["failed_controls"],
        control_details=eval_res["control_details"],
        audited_by=eval_res["audited_by"],
    )
    return await repo.save_compliance_report(report)


@router.get("/reports", response_model=list[ComplianceReportOut])
async def list_compliance_reports(
    framework: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List historical compliance audit reports."""
    repo = ProductionRepository(db)
    return await repo.list_compliance_reports(framework=framework)


@router.post("/gdpr-forget")
async def execute_gdpr_data_deletion(payload: GDPRDataDeletionRequest):
    """Executes GDPR right-to-be-forgotten user data anonymization."""
    return comp_service.process_gdpr_forget_request(payload.user_email)
