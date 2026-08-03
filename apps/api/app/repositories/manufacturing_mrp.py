import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.manufacturing_mrp_v13 import (
    BillOfMaterial,
    BOMItem,
    FinishedGood,
    Machine,
    MachineDowntime,
    MachineMaintenance,
    MaterialConsumption,
    MRPRun,
    ProductFamily,
    ProductionOrder,
    QualityInspection,
    WorkCenter,
)
from app.repositories.base import BaseRepository


class ProductFamilyRepository(BaseRepository[ProductFamily]):
    def __init__(self, db: AsyncSession):
        super().__init__(ProductFamily, db)

    async def find_by_code(self, org_id: uuid.UUID, code: str) -> ProductFamily | None:
        stmt = select(ProductFamily).where(
            ProductFamily.organization_id == org_id, ProductFamily.family_code == code, ProductFamily.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class BOMRepository(BaseRepository[BillOfMaterial]):
    def __init__(self, db: AsyncSession):
        super().__init__(BillOfMaterial, db)

    async def get_with_items(self, bom_id: uuid.UUID) -> BillOfMaterial | None:
        stmt = (
            select(BillOfMaterial)
            .options(selectinload(BillOfMaterial.items))
            .where(BillOfMaterial.id == bom_id, BillOfMaterial.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def find_by_code(self, code: str) -> BillOfMaterial | None:
        stmt = select(BillOfMaterial).where(
            BillOfMaterial.bom_code == code, BillOfMaterial.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def find_by_product(self, product_id: uuid.UUID) -> BillOfMaterial | None:
        stmt = (
            select(BillOfMaterial)
            .options(selectinload(BillOfMaterial.items))
            .where(BillOfMaterial.product_id == product_id, BillOfMaterial.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class WorkCenterRepository(BaseRepository[WorkCenter]):
    def __init__(self, db: AsyncSession):
        super().__init__(WorkCenter, db)

    async def find_by_code(self, org_id: uuid.UUID, code: str) -> WorkCenter | None:
        stmt = select(WorkCenter).where(
            WorkCenter.organization_id == org_id, WorkCenter.center_code == code, WorkCenter.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_org(self, org_id: uuid.UUID) -> list[WorkCenter]:
        stmt = select(WorkCenter).where(
            WorkCenter.organization_id == org_id, WorkCenter.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class MachineRepository(BaseRepository[Machine]):
    def __init__(self, db: AsyncSession):
        super().__init__(Machine, db)

    async def find_by_code(self, code: str) -> Machine | None:
        stmt = select(Machine).where(
            Machine.machine_code == code, Machine.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class MachineMaintenanceRepository(BaseRepository[MachineMaintenance]):
    def __init__(self, db: AsyncSession):
        super().__init__(MachineMaintenance, db)


class ProductionOrderRepository(BaseRepository[ProductionOrder]):
    def __init__(self, db: AsyncSession):
        super().__init__(ProductionOrder, db)

    async def find_by_number(self, num: str) -> ProductionOrder | None:
        stmt = select(ProductionOrder).where(
            ProductionOrder.production_number == num, ProductionOrder.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_org(self, org_id: uuid.UUID) -> list[ProductionOrder]:
        stmt = select(ProductionOrder).where(
            ProductionOrder.organization_id == org_id, ProductionOrder.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class QualityInspectionRepository(BaseRepository[QualityInspection]):
    def __init__(self, db: AsyncSession):
        super().__init__(QualityInspection, db)


class MRPRunRepository(BaseRepository[MRPRun]):
    def __init__(self, db: AsyncSession):
        super().__init__(MRPRun, db)
