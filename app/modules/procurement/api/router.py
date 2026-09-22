"""Procurement Domain Central API Router."""

from fastapi import APIRouter

from app.modules.procurement.api.v1.purchase_order_endpoints import router as po_router
from app.modules.procurement.api.v1.purchase_request_endpoints import router as pr_router
from app.modules.procurement.api.v1.supplier_endpoints import router as supplier_router

router = APIRouter()

router.include_router(supplier_router)
router.include_router(pr_router)
router.include_router(po_router)
