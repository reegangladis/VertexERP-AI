import uuid
from typing import List, Optional, Tuple, Any
from datetime import datetime, date
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.manufacturing import (
    ProductFamily,
    ProductVersion,
    BillOfMaterial,
    BOMItem,
    Routing,
    RoutingOperation,
    WorkCenter,
    Machine,
    ProductionOrder,
    ProductionOrderItem,
    ProductionLog,
    MaterialConsumption,
    QualityInspection,
    QualityResult,
    MaintenanceRequest,
    MaintenanceLog,
    MachineDowntime,
    MRPRun,
)


class BillOfMaterialRepository(BaseRepository[BillOfMaterial]):
    def __init__(self, db: AsyncSession):
        super().__init__(BillOfMaterial, db)

    async def get_with_items(self, bom_id: uuid.UUID) -> Optional[BillOfMaterial]:
        stmt = (
            select(BillOfMaterial)
            .where(BillOfMaterial.id == bom_id, BillOfMaterial.is_deleted == False)
            .options(selectinload(BillOfMaterial.items))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_product(self, organization_id: uuid.UUID, product_id: uuid.UUID) -> List[BillOfMaterial]:
        stmt = (
            select(BillOfMaterial)
            .where(
                BillOfMaterial.organization_id == organization_id,
                BillOfMaterial.product_id == product_id,
                BillOfMaterial.is_deleted == False,
            )
            .options(selectinload(BillOfMaterial.items))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class RoutingRepository(BaseRepository[Routing]):
    def __init__(self, db: AsyncSession):
        super().__init__(Routing, db)

    async def get_with_operations(self, routing_id: uuid.UUID) -> Optional[Routing]:
        stmt = (
            select(Routing)
            .where(Routing.id == routing_id, Routing.is_deleted == False)
            .options(selectinload(Routing.operations))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class WorkCenterRepository(BaseRepository[WorkCenter]):
    def __init__(self, db: AsyncSession):
        super().__init__(WorkCenter, db)

    async def get_with_machines(self, work_center_id: uuid.UUID) -> Optional[WorkCenter]:
        stmt = (
            select(WorkCenter)
            .where(WorkCenter.id == work_center_id, WorkCenter.is_deleted == False)
            .options(selectinload(WorkCenter.machines))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class MachineRepository(BaseRepository[Machine]):
    def __init__(self, db: AsyncSession):
        super().__init__(Machine, db)


class ProductionOrderRepository(BaseRepository[ProductionOrder]):
    def __init__(self, db: AsyncSession):
        super().__init__(ProductionOrder, db)

    async def get_with_items(self, order_id: uuid.UUID) -> Optional[ProductionOrder]:
        stmt = (
            select(ProductionOrder)
            .where(ProductionOrder.id == order_id, ProductionOrder.is_deleted == False)
            .options(selectinload(ProductionOrder.items))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_number(self, organization_id: uuid.UUID, order_number: str) -> Optional[ProductionOrder]:
        stmt = select(ProductionOrder).where(
            ProductionOrder.organization_id == organization_id,
            ProductionOrder.order_number == order_number,
            ProductionOrder.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class QualityInspectionRepository(BaseRepository[QualityInspection]):
    def __init__(self, db: AsyncSession):
        super().__init__(QualityInspection, db)

    async def get_with_results(self, inspection_id: uuid.UUID) -> Optional[QualityInspection]:
        stmt = (
            select(QualityInspection)
            .where(QualityInspection.id == inspection_id, QualityInspection.is_deleted == False)
            .options(selectinload(QualityInspection.results))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class MaintenanceRequestRepository(BaseRepository[MaintenanceRequest]):
    def __init__(self, db: AsyncSession):
        super().__init__(MaintenanceRequest, db)


class MRPRunRepository(BaseRepository[MRPRun]):
    def __init__(self, db: AsyncSession):
        super().__init__(MRPRun, db)
