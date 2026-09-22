"""Centralized Router for the Manufacturing & MRP Domain."""

from fastapi import APIRouter

from app.modules.manufacturing.api.bom_endpoints import router as bom_router
from app.modules.manufacturing.api.mrp_endpoints import router as mrp_router
from app.modules.manufacturing.api.production_endpoints import router as production_router
from app.modules.manufacturing.api.quality_endpoints import router as quality_router
from app.modules.manufacturing.api.routing_endpoints import router as routing_router
from app.modules.manufacturing.api.work_center_endpoints import router as work_center_router

mfg_router = APIRouter(prefix="/manufacturing", tags=["Manufacturing & MRP Domain"])

mfg_router.include_router(work_center_router)
mfg_router.include_router(routing_router)
mfg_router.include_router(bom_router)
mfg_router.include_router(production_router)
mfg_router.include_router(mrp_router)
mfg_router.include_router(quality_router)
