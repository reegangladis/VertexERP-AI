"""API Version 1 Central Router Registry."""

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.modules.ai.api.router import ai_router
from app.modules.analytics.api.router import analytics_router
from app.modules.crm.api.router import router as crm_router
from app.modules.finance.api.router import router as finance_router
from app.modules.hr.api.router import router as hr_router
from app.modules.identity.api.router import router as identity_router
from app.modules.inventory.api.router import router as inventory_router
from app.modules.jobs.api import jobs_router
from app.modules.manufacturing.api.router import mfg_router as manufacturing_router
from app.modules.organization.api.router import router as organization_router
from app.modules.procurement.api.router import router as procurement_router

api_v1_router = APIRouter(prefix="/api/v1")

# Mount foundational routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(identity_router)
api_v1_router.include_router(organization_router)
api_v1_router.include_router(hr_router)
api_v1_router.include_router(crm_router)
api_v1_router.include_router(inventory_router)
api_v1_router.include_router(procurement_router)
api_v1_router.include_router(finance_router)
api_v1_router.include_router(manufacturing_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(jobs_router)
