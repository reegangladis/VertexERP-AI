"""Inventory Domain Central API Router."""

from fastapi import APIRouter

from app.modules.inventory.api.v1.category_endpoints import router as category_router
from app.modules.inventory.api.v1.goods_receipt_endpoints import router as gr_router
from app.modules.inventory.api.v1.product_endpoints import router as product_router
from app.modules.inventory.api.v1.stock_adjustment_endpoints import router as adj_router
from app.modules.inventory.api.v1.stock_balance_endpoints import router as balance_router
from app.modules.inventory.api.v1.stock_movement_endpoints import router as movement_router
from app.modules.inventory.api.v1.stock_transfer_endpoints import router as transfer_router
from app.modules.inventory.api.v1.uom_endpoints import router as uom_router
from app.modules.inventory.api.v1.warehouse_endpoints import router as warehouse_router

router = APIRouter()

router.include_router(uom_router)
router.include_router(category_router)
router.include_router(product_router)
router.include_router(warehouse_router)
router.include_router(balance_router)
router.include_router(movement_router)
router.include_router(transfer_router)
router.include_router(adj_router)
router.include_router(gr_router)
