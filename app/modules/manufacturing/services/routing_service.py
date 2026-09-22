"""Routing Domain Service."""

import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.manufacturing.models.routing import Routing, RoutingOperation
from app.modules.manufacturing.repositories.routing_repository import RoutingRepository
from app.modules.manufacturing.repositories.work_center_repository import WorkCenterRepository
from app.modules.manufacturing.schemas.routing import (
    RoutingCreate,
    RoutingOperationCreate,
)


class RoutingService:
    """Domain service managing manufacturing routings and work center operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.routing_repo = RoutingRepository(session)
        self.work_center_repo = WorkCenterRepository(session)

    async def create_routing(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: RoutingCreate
    ) -> Routing:
        routing = Routing(
            tenant_id=tenant_id,
            organization_id=org_id,
            code=data.code,
            name=data.name,
            product_id=data.product_id,
            description=data.description,
            version=data.version,
            is_active=data.is_active,
        )

        for op_data in data.operations:
            # Validate work center exists
            wc = await self.work_center_repo.get_work_center_by_id(
                op_data.work_center_id, tenant_id, org_id
            )
            if not wc:
                raise NotFoundException(f"Work Center {op_data.work_center_id} not found.")

            op = RoutingOperation(
                tenant_id=tenant_id,
                organization_id=org_id,
                sequence=op_data.sequence,
                operation_name=op_data.operation_name,
                work_center_id=op_data.work_center_id,
                preferred_machine_id=op_data.preferred_machine_id,
                setup_time_hours=op_data.setup_time_hours,
                run_time_per_unit_hours=op_data.run_time_per_unit_hours,
                description=op_data.description,
            )
            routing.operations.append(op)

        await self.routing_repo.create_routing(routing)
        return routing

    async def estimate_routing_time_and_cost(
        self, routing_id: uuid.UUID, quantity: Decimal, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> tuple[Decimal, Decimal]:
        """Calculates total estimated hours and standard labor/machine cost for given quantity."""
        routing = await self.routing_repo.get_routing_by_id(routing_id, tenant_id, org_id)
        if not routing:
            raise NotFoundException(f"Routing {routing_id} not found.")

        total_hours = Decimal("0.00")
        total_cost = Decimal("0.00")

        for op in routing.operations:
            op_hours = op.setup_time_hours + (op.run_time_per_unit_hours * quantity)
            total_hours += op_hours

            wc = await self.work_center_repo.get_work_center_by_id(
                op.work_center_id, tenant_id, org_id
            )
            if wc:
                rate = wc.cost_per_hour + wc.overhead_cost_per_hour
                total_cost += op_hours * rate

        return total_hours, total_cost

    async def add_operation(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: RoutingOperationCreate
    ) -> RoutingOperation:
        if not data.routing_id:
            raise NotFoundException("routing_id is required.")
        routing = await self.routing_repo.get_routing_by_id(data.routing_id, tenant_id, org_id)
        if not routing:
            raise NotFoundException(f"Routing {data.routing_id} not found.")

        wc = await self.work_center_repo.get_work_center_by_id(
            data.work_center_id, tenant_id, org_id
        )
        if not wc:
            raise NotFoundException(f"Work Center {data.work_center_id} not found.")

        op = RoutingOperation(
            tenant_id=tenant_id,
            organization_id=org_id,
            routing_id=data.routing_id,
            sequence=data.sequence,
            operation_name=data.operation_name,
            work_center_id=data.work_center_id,
            preferred_machine_id=data.preferred_machine_id,
            setup_time_hours=data.setup_time_hours,
            run_time_per_unit_hours=data.run_time_per_unit_hours,
            description=data.description,
        )
        await self.routing_repo.create_operation(op)
        return op

