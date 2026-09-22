"""Quality Inspection Domain Service."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.manufacturing.models.quality import QualityInspection
from app.modules.manufacturing.repositories.production_order_repository import (
    ProductionOrderRepository,
)
from app.modules.manufacturing.repositories.quality_repository import QualityRepository
from app.modules.manufacturing.schemas.quality import (
    QualityInspectionCreate,
)


class QualityService:
    """Domain service managing Quality Control inspections and disposition."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.quality_repo = QualityRepository(session)
        self.order_repo = ProductionOrderRepository(session)

    async def create_inspection(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: QualityInspectionCreate,
        inspector_id: uuid.UUID | None = None,
    ) -> QualityInspection:
        # Validate production order
        order = await self.order_repo.get_order_by_id(data.production_order_id, tenant_id, org_id)
        if not order:
            raise NotFoundException(f"Production Order {data.production_order_id} not found.")

        inspection_number = (
            f"QC-{datetime.now(UTC).strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        )

        passed = data.passed_quantity or data.inspected_quantity
        failed = data.failed_quantity or Decimal("0.0000")

        # Determine result if not provided
        result = data.result
        if failed > 0 and passed == 0:
            result = "FAILED"
        elif failed > 0 and passed > 0:
            result = "CONDITIONALLY_PASSED"
        else:
            result = "PASSED"

        inspection = QualityInspection(
            tenant_id=tenant_id,
            organization_id=org_id,
            inspection_number=inspection_number,
            production_order_id=data.production_order_id,
            work_order_id=data.work_order_id,
            product_id=data.product_id,
            inspection_type=data.inspection_type,
            inspected_quantity=data.inspected_quantity,
            passed_quantity=passed,
            failed_quantity=failed,
            result=result,
            inspector_id=inspector_id,
            inspection_date=datetime.now(UTC),
            defect_reason=data.defect_reason,
            notes=data.notes,
            status="COMPLETED",
        )

        if failed > 0:
            order.rejected_quantity += failed

        await self.quality_repo.create_inspection(inspection)
        await self.session.flush()
        return inspection
