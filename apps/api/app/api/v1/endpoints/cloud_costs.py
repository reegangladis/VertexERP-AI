import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.repositories.cloud_release_repository import CloudReleaseRepository
from app.services.finops_service import FinOpsService
from app.models.cloud_release import CostReport
from app.schemas.cloud_release import CostReportOut

router = APIRouter()
finops_service = FinOpsService()


@router.get("/summary", response_model=CostReportOut)
async def get_monthly_cost_summary(db: AsyncSession = Depends(get_db)):
    """Returns FinOps cloud cost breakdown, budget utilization, and savings recommendations."""
    repo = CloudReleaseRepository(db)
    res = finops_service.get_monthly_cost_summary()

    report = CostReport(
        month_year=res["month_year"],
        provider=res["provider"],
        total_cost_usd=res["total_cost_usd"],
        monthly_budget_usd=res["monthly_budget_usd"],
        service_breakdown=res["service_breakdown"],
        recommendations=res["recommendations"],
        budget_utilized_percent=res["budget_utilized_percent"],
    )
    return await repo.save_cost_report(report)


@router.get("/budget-alert")
async def evaluate_budget_alert(
    current_spend: float = Query(38450.0),
    budget: float = Query(50000.0),
):
    """Evaluates budget threshold alerts."""
    return finops_service.evaluate_budget_alert(current_spend, budget)
