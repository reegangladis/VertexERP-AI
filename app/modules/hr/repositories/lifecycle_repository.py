"""Lifecycle, Contracts, and Onboarding repository."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hr.models.lifecycle import (
    EmployeeLifecycleEvent,
    EmploymentContract,
    OnboardingTask,
)


class LifecycleRepository:
    """Repository for Employment Lifecycle persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Contracts
    async def get_contract(
        self, contract_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> EmploymentContract | None:
        stmt = select(EmploymentContract).where(
            EmploymentContract.id == contract_id,
            EmploymentContract.tenant_id == tenant_id,
            EmploymentContract.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_contract_by_number(
        self, contract_number: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> EmploymentContract | None:
        stmt = select(EmploymentContract).where(
            EmploymentContract.contract_number == contract_number,
            EmploymentContract.tenant_id == tenant_id,
            EmploymentContract.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_contracts_for_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmploymentContract]:
        stmt = (
            select(EmploymentContract)
            .where(
                EmploymentContract.employee_id == employee_id,
                EmploymentContract.tenant_id == tenant_id,
                EmploymentContract.organization_id == org_id,
            )
            .order_by(EmploymentContract.start_date.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_contract(self, contract: EmploymentContract) -> EmploymentContract:
        self.session.add(contract)
        await self.session.flush()
        return contract

    async def update_contract(self, contract: EmploymentContract) -> EmploymentContract:
        contract.updated_at = datetime.now(UTC)
        contract.version += 1
        await self.session.flush()
        return contract

    # Lifecycle Events
    async def list_events_for_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmployeeLifecycleEvent]:
        stmt = (
            select(EmployeeLifecycleEvent)
            .where(
                EmployeeLifecycleEvent.employee_id == employee_id,
                EmployeeLifecycleEvent.tenant_id == tenant_id,
                EmployeeLifecycleEvent.organization_id == org_id,
            )
            .order_by(
                EmployeeLifecycleEvent.effective_date.desc(),
                EmployeeLifecycleEvent.created_at.desc(),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_event(self, event: EmployeeLifecycleEvent) -> EmployeeLifecycleEvent:
        self.session.add(event)
        await self.session.flush()
        return event

    # Onboarding Tasks
    async def get_task(
        self, task_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> OnboardingTask | None:
        stmt = select(OnboardingTask).where(
            OnboardingTask.id == task_id,
            OnboardingTask.tenant_id == tenant_id,
            OnboardingTask.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_tasks_for_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[OnboardingTask]:
        stmt = (
            select(OnboardingTask)
            .where(
                OnboardingTask.employee_id == employee_id,
                OnboardingTask.tenant_id == tenant_id,
                OnboardingTask.organization_id == org_id,
            )
            .order_by(OnboardingTask.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_task(self, task: OnboardingTask) -> OnboardingTask:
        self.session.add(task)
        await self.session.flush()
        return task

    async def update_task(self, task: OnboardingTask) -> OnboardingTask:
        await self.session.flush()
        return task
