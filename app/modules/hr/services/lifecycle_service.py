"""Lifecycle, Contracts, and Onboarding service."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.hr.models.lifecycle import (
    EmployeeLifecycleEvent,
    EmploymentContract,
    OnboardingTask,
)
from app.modules.hr.repositories.employee_repository import EmployeeRepository
from app.modules.hr.repositories.lifecycle_repository import LifecycleRepository
from app.modules.hr.schemas.lifecycle import (
    EmploymentContractCreate,
    EmploymentContractUpdate,
    LifecycleEventCreate,
    OnboardingTaskCreate,
    OnboardingTaskUpdate,
)


class LifecycleService:
    """Business service for Contracts, Lifecycle transitions, and Onboarding."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.lifecycle_repo = LifecycleRepository(session)
        self.employee_repo = EmployeeRepository(session)

    async def _ensure_employee_exists(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> None:
        emp = await self.employee_repo.get_by_id(employee_id, tenant_id, org_id)
        if not emp:
            raise NotFoundException(f"Employee '{employee_id}' not found")

    # Contracts
    async def create_contract(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: EmploymentContractCreate
    ) -> EmploymentContract:
        await self._ensure_employee_exists(data.employee_id, tenant_id, org_id)
        existing = await self.lifecycle_repo.get_contract_by_number(
            data.contract_number, tenant_id, org_id
        )
        if existing:
            raise ConflictException(f"Contract number '{data.contract_number}' already exists")

        contract = EmploymentContract(
            tenant_id=tenant_id,
            organization_id=org_id,
            employee_id=data.employee_id,
            contract_number=data.contract_number,
            contract_type=data.contract_type,
            start_date=data.start_date,
            end_date=data.end_date,
            probation_end_date=data.probation_end_date,
            notice_period_days=data.notice_period_days,
            base_salary=data.base_salary,
            currency=data.currency,
            terms_and_conditions=data.terms_and_conditions,
            status=data.status,
        )
        return await self.lifecycle_repo.create_contract(contract)

    async def get_contract(
        self, contract_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> EmploymentContract:
        contract = await self.lifecycle_repo.get_contract(contract_id, tenant_id, org_id)
        if not contract:
            raise NotFoundException(f"Contract '{contract_id}' not found")
        return contract

    async def list_contracts_for_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmploymentContract]:
        await self._ensure_employee_exists(employee_id, tenant_id, org_id)
        return await self.lifecycle_repo.list_contracts_for_employee(employee_id, tenant_id, org_id)

    async def update_contract(
        self,
        contract_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: EmploymentContractUpdate,
    ) -> EmploymentContract:
        contract = await self.get_contract(contract_id, tenant_id, org_id)
        if data.contract_type is not None:
            contract.contract_type = data.contract_type
        if data.start_date is not None:
            contract.start_date = data.start_date
        if data.end_date is not None:
            contract.end_date = data.end_date
        if data.probation_end_date is not None:
            contract.probation_end_date = data.probation_end_date
        if data.notice_period_days is not None:
            contract.notice_period_days = data.notice_period_days
        if data.base_salary is not None:
            contract.base_salary = data.base_salary
        if data.currency is not None:
            contract.currency = data.currency
        if data.terms_and_conditions is not None:
            contract.terms_and_conditions = data.terms_and_conditions
        if data.status is not None:
            contract.status = data.status
        return await self.lifecycle_repo.update_contract(contract)

    # Lifecycle Events
    async def record_lifecycle_event(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        user_id: uuid.UUID | None,
        data: LifecycleEventCreate,
    ) -> EmployeeLifecycleEvent:
        await self._ensure_employee_exists(data.employee_id, tenant_id, org_id)
        event = EmployeeLifecycleEvent(
            tenant_id=tenant_id,
            organization_id=org_id,
            employee_id=data.employee_id,
            event_type=data.event_type,
            effective_date=data.effective_date,
            previous_value_json=data.previous_value_json,
            new_value_json=data.new_value_json,
            remarks=data.remarks,
            processed_by_id=user_id,
        )
        return await self.lifecycle_repo.create_event(event)

    async def list_lifecycle_events(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmployeeLifecycleEvent]:
        await self._ensure_employee_exists(employee_id, tenant_id, org_id)
        return await self.lifecycle_repo.list_events_for_employee(employee_id, tenant_id, org_id)

    # Onboarding Tasks
    async def create_onboarding_task(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: OnboardingTaskCreate
    ) -> OnboardingTask:
        await self._ensure_employee_exists(data.employee_id, tenant_id, org_id)
        task = OnboardingTask(
            tenant_id=tenant_id,
            organization_id=org_id,
            employee_id=data.employee_id,
            title=data.title,
            description=data.description,
            category=data.category,
            due_date=data.due_date,
            assigned_to_id=data.assigned_to_id,
        )
        return await self.lifecycle_repo.create_task(task)

    async def list_onboarding_tasks(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[OnboardingTask]:
        await self._ensure_employee_exists(employee_id, tenant_id, org_id)
        return await self.lifecycle_repo.list_tasks_for_employee(employee_id, tenant_id, org_id)

    async def update_onboarding_task(
        self,
        task_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: OnboardingTaskUpdate,
    ) -> OnboardingTask:
        task = await self.lifecycle_repo.get_task(task_id, tenant_id, org_id)
        if not task:
            raise NotFoundException(f"Task '{task_id}' not found")
        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.category is not None:
            task.category = data.category
        if data.due_date is not None:
            task.due_date = data.due_date
        if data.status is not None:
            task.status = data.status
            if data.status == "COMPLETED" and not task.completed_at:
                task.completed_at = datetime.now(UTC)
        if data.assigned_to_id is not None:
            task.assigned_to_id = data.assigned_to_id
        return await self.lifecycle_repo.update_task(task)
