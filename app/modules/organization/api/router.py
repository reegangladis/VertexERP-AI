"""Aggregated Organization module router."""

from fastapi import APIRouter

from app.modules.organization.api.v1.branch_endpoints import router as branch_router
from app.modules.organization.api.v1.business_unit_endpoints import router as bu_router
from app.modules.organization.api.v1.calendar_endpoints import router as cal_router
from app.modules.organization.api.v1.cost_center_endpoints import router as cc_router
from app.modules.organization.api.v1.department_endpoints import router as dept_router
from app.modules.organization.api.v1.designation_endpoints import router as desig_router
from app.modules.organization.api.v1.holiday_endpoints import router as holiday_router
from app.modules.organization.api.v1.location_endpoints import router as loc_router
from app.modules.organization.api.v1.organization_endpoints import router as org_router
from app.modules.organization.api.v1.team_endpoints import router as team_router

router = APIRouter()
router.include_router(org_router)
router.include_router(branch_router)
router.include_router(dept_router)
router.include_router(team_router)
router.include_router(desig_router)
router.include_router(bu_router)
router.include_router(cc_router)
router.include_router(loc_router)
router.include_router(cal_router)
router.include_router(holiday_router)
