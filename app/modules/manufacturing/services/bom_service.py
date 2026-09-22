"""BOM Domain Service."""

import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.inventory.repositories.product_repository import ProductRepository
from app.modules.manufacturing.models.bom import BillOfMaterial, BOMComponent, BOMVersion
from app.modules.manufacturing.repositories.bom_repository import BOMRepository
from app.modules.manufacturing.schemas.bom import (
    BillOfMaterialCreate,
    BOMComponentCreate,
    BOMVersionCreate,
)


class BOMService:
    """Domain service managing multi-level Bills of Materials and versioning."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.bom_repo = BOMRepository(session)
        self.product_repo = ProductRepository(session)

    async def create_bom(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: BillOfMaterialCreate
    ) -> BillOfMaterial:
        # Validate finished/assembly product
        product = await self.product_repo.get_by_id(data.product_id, tenant_id, org_id)
        if not product:
            raise NotFoundException(f"Product {data.product_id} not found.")

        # Create BOM header
        bom = BillOfMaterial(
            tenant_id=tenant_id,
            organization_id=org_id,
            code=data.code,
            name=data.name,
            product_id=data.product_id,
            routing_id=data.routing_id,
            quantity=data.quantity,
            uom_id=data.uom_id,
            status=data.status,
            is_default=data.is_default,
            notes=data.notes,
        )

        # Create initial Version 1
        v1 = BOMVersion(
            tenant_id=tenant_id,
            organization_id=org_id,
            version_number=1,
            revision_notes="Initial BOM release",
            status="ACTIVE",
        )

        for comp_data in data.components:
            comp_product = await self.product_repo.get_by_id(
                comp_data.component_product_id, tenant_id, org_id
            )
            if not comp_product:
                raise NotFoundException(
                    f"Component product {comp_data.component_product_id} not found."
                )

            comp = BOMComponent(
                tenant_id=tenant_id,
                organization_id=org_id,
                component_product_id=comp_data.component_product_id,
                quantity=comp_data.quantity,
                uom_id=comp_data.uom_id,
                scrap_percentage=comp_data.scrap_percentage,
                operation_sequence=comp_data.operation_sequence,
                position=comp_data.position,
                notes=comp_data.notes,
            )
            v1.components.append(comp)

        bom.versions.append(v1)
        await self.bom_repo.create_bom(bom)
        return bom

    async def add_version(
        self,
        bom_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: BOMVersionCreate,
    ) -> BOMVersion:
        bom = await self.bom_repo.get_bom_by_id(bom_id, tenant_id, org_id)
        if not bom:
            raise NotFoundException(f"BOM {bom_id} not found.")

        # Determine next version number
        next_version = len(bom.versions) + 1 if not data.version_number else data.version_number

        version = BOMVersion(
            tenant_id=tenant_id,
            organization_id=org_id,
            bom_id=bom_id,
            version_number=next_version,
            revision_notes=data.revision_notes,
            status=data.status,
            effective_from_date=data.effective_from_date,
            effective_to_date=data.effective_to_date,
        )

        for comp_data in data.components:
            comp = BOMComponent(
                tenant_id=tenant_id,
                organization_id=org_id,
                component_product_id=comp_data.component_product_id,
                quantity=comp_data.quantity,
                uom_id=comp_data.uom_id,
                scrap_percentage=comp_data.scrap_percentage,
                operation_sequence=comp_data.operation_sequence,
                position=comp_data.position,
                notes=comp_data.notes,
            )
            version.components.append(comp)

        await self.bom_repo.create_version(version)
        return version

    async def calculate_bom_theoretical_cost(
        self, bom_version_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Decimal:
        """Calculates theoretical raw material cost for 1 unit based on current product average costs."""
        version = await self.bom_repo.get_version_by_id(bom_version_id, tenant_id, org_id)
        if not version:
            raise NotFoundException(f"BOM Version {bom_version_id} not found.")

        total_cost = Decimal("0.0000")
        for comp in version.components:
            prod = await self.product_repo.get_by_id(comp.component_product_id, tenant_id, org_id)
            if prod:
                qty_with_scrap = comp.quantity * (1 + (comp.scrap_percentage / Decimal("100.00")))
                cost = getattr(
                    prod, "cost_price", getattr(prod, "standard_cost", Decimal("0.0000"))
                )
                total_cost += qty_with_scrap * cost
        return total_cost

    async def add_component_to_version(
        self,
        bom_version_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: BOMComponentCreate,
    ) -> BOMComponent:
        version = await self.bom_repo.get_version_by_id(bom_version_id, tenant_id, org_id)
        if not version:
            raise NotFoundException(f"BOM Version {bom_version_id} not found.")

        comp_product = await self.product_repo.get_by_id(
            data.component_product_id, tenant_id, org_id
        )
        if not comp_product:
            raise NotFoundException(
                f"Component product {data.component_product_id} not found."
            )

        comp = BOMComponent(
            tenant_id=tenant_id,
            organization_id=org_id,
            bom_version_id=bom_version_id,
            component_product_id=data.component_product_id,
            quantity=data.quantity,
            uom_id=data.uom_id,
            scrap_percentage=data.scrap_percentage,
            operation_sequence=data.operation_sequence,
            position=data.position,
            notes=data.notes,
        )
        await self.bom_repo.create_component(comp)
        return comp

