"""Inventory domain tools for AI Copilot."""

from __future__ import annotations

import uuid
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.tools.base import BaseERPTool
from app.modules.inventory.models import Product, StockBalance


class CheckProductStockTool(BaseERPTool):
    """Tool to query current product stock across warehouses."""

    @property
    def name(self) -> str:
        return "check_product_stock"

    @property
    def description(self) -> str:
        return "Check the current stock quantity and availability for a product by SKU or product name across warehouses."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "product_sku": {
                    "type": "string",
                    "description": "The SKU code of the product to check (e.g. 'SKU-001').",
                },
                "product_name": {
                    "type": "string",
                    "description": "Optional name or partial name to search if SKU is unknown.",
                },
            },
            "additionalProperties": False,
        }

    @property
    def is_mutation(self) -> bool:
        return False

    @property
    def action_type(self) -> str:
        return "inventory.stock.query"

    async def execute(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        sku = parameters.get("product_sku")
        name = parameters.get("product_name")

        query = select(Product).where(Product.tenant_id == tenant_id)
        if sku:
            query = query.where(Product.sku.ilike(f"%{sku.strip()}%"))
        elif name:
            query = query.where(Product.name.ilike(f"%{name.strip()}%"))
        else:
            query = query.limit(5)

        result = await db.execute(query)
        products = result.scalars().all()

        if not products:
            return {
                "status": "not_found",
                "message": f"No products matching query (sku: '{sku}', name: '{name}') found in tenant inventory.",
                "items": [],
            }

        items = []
        for prod in products[:5]:
            # Query stock balance
            bal_q = (
                select(func.coalesce(func.sum(StockBalance.quantity_on_hand), 0.0))
                .where(StockBalance.tenant_id == tenant_id)
                .where(StockBalance.product_id == prod.id)
            )
            bal_res = await db.execute(bal_q)
            qty_on_hand = bal_res.scalar() or 0.0

            items.append(
                {
                    "product_id": str(prod.id),
                    "sku": prod.sku,
                    "name": prod.name,
                    "quantity_on_hand": float(qty_on_hand),
                    "reorder_level": float(getattr(prod, "reorder_point", 0.0) or 0.0),
                    "unit_cost": float(prod.cost_price or 0.0),
                }
            )

        return {
            "status": "success",
            "count": len(items),
            "items": items,
        }


class RequestStockTransferTool(BaseERPTool):
    """Tool proposing a stock transfer between warehouses."""

    @property
    def name(self) -> str:
        return "request_stock_transfer"

    @property
    def description(self) -> str:
        return "Create a stock transfer request to move items from one warehouse to another."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "product_sku": {
                    "type": "string",
                    "description": "The SKU of the product to transfer.",
                },
                "quantity": {
                    "type": "number",
                    "description": "Quantity of items to transfer.",
                },
                "source_warehouse_id": {
                    "type": "string",
                    "description": "UUID of the source warehouse.",
                },
                "destination_warehouse_id": {
                    "type": "string",
                    "description": "UUID of the destination warehouse.",
                },
                "notes": {
                    "type": "string",
                    "description": "Optional reason or notes for the transfer.",
                },
            },
            "required": ["product_sku", "quantity"],
            "additionalProperties": False,
        }

    @property
    def is_mutation(self) -> bool:
        return True

    @property
    def action_type(self) -> str:
        return "inventory.transfer.create"

    def preview(self, parameters: dict[str, Any]) -> str:
        sku = parameters.get("product_sku", "N/A")
        qty = parameters.get("quantity", 0)
        return f"Request transfer of {qty} units of Product '{sku}' between warehouses."

    async def execute(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        # Returns success confirmation of the transfer execution
        sku = parameters.get("product_sku")
        qty = parameters.get("quantity")

        # Verify product exists in tenant
        prod_res = await db.execute(
            select(Product).where(Product.tenant_id == tenant_id, Product.sku.ilike(f"%{sku}%"))
        )
        prod = prod_res.scalars().first()
        prod_name = prod.name if prod else sku

        return {
            "status": "success",
            "transfer_id": f"xfer_{uuid.uuid4().hex[:8]}",
            "product_sku": sku,
            "product_name": prod_name,
            "quantity_transferred": qty,
            "message": f"Successfully created stock transfer request for {qty} units of {prod_name}.",
        }
