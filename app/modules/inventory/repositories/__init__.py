"""Inventory Domain Repositories."""

from app.modules.inventory.repositories.goods_receipt_repository import GoodsReceiptRepository
from app.modules.inventory.repositories.product_repository import ProductRepository
from app.modules.inventory.repositories.stock_adjustment_repository import StockAdjustmentRepository
from app.modules.inventory.repositories.stock_balance_repository import StockBalanceRepository
from app.modules.inventory.repositories.stock_movement_repository import StockMovementRepository
from app.modules.inventory.repositories.stock_transfer_repository import StockTransferRepository
from app.modules.inventory.repositories.uom_repository import CategoryRepository, UomRepository
from app.modules.inventory.repositories.warehouse_repository import (
    LocationRepository,
    WarehouseRepository,
)

__all__ = [
    "UomRepository",
    "CategoryRepository",
    "ProductRepository",
    "WarehouseRepository",
    "LocationRepository",
    "StockBalanceRepository",
    "StockMovementRepository",
    "StockTransferRepository",
    "StockAdjustmentRepository",
    "GoodsReceiptRepository",
]
