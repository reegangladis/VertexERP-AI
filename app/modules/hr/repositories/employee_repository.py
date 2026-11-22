"""Employee repository."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hr.models.employee import Employee


class EmployeeRepository:
    """Repository for Employee persistence with strict multi-tenant & organization isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Employee | None:
        stmt = select(Employee).where(
            Employee.id == employee_id,
            Employee.tenant_id == tenant_id,
            Employee.organization_id == org_id,
            Employee.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_number(
        self, employee_number: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Employee | None:
        stmt = select(Employee).where(
            Employee.employee_number == employee_number,
            Employee.tenant_id == tenant_id,
            Employee.organization_id == org_id,
            Employee.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(
        self, email: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Employee | None:
        stmt = select(Employee).where(
            Employee.email == email.lower(),
            Employee.tenant_id == tenant_id,
            Employee.organization_id == org_id,
            Employee.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_org(self, tenant_id: uuid.UUID, org_id: uuid.UUID) -> int:
        stmt = select(func.count(Employee.id)).where(
            Employee.tenant_id == tenant_id,
            Employee.organization_id == org_id,
            Employee.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def list_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        department_id: uuid.UUID | None = None,
        branch_id: uuid.UUID | None = None,
        designation_id: uuid.UUID | None = None,
        status: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> Sequence[Employee]:
        stmt = select(Employee).where(
            Employee.tenant_id == tenant_id,
            Employee.organization_id == org_id,
            Employee.is_deleted.is_(False),
        )
        if department_id is not None:
            stmt = stmt.where(Employee.department_id == department_id)
        if branch_id is not None:
            stmt = stmt.where(Employee.branch_id == branch_id)
        if designation_id is not None:
            stmt = stmt.where(Employee.designation_id == designation_id)
        if status is not None:
            stmt = stmt.where(Employee.employment_status == status)
        if is_active is not None:
            stmt = stmt.where(Employee.is_active.is_(is_active))
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                (Employee.first_name.ilike(pattern))
                | (Employee.last_name.ilike(pattern))
                | (Employee.email.ilike(pattern))
                | (Employee.employee_number.ilike(pattern))
            )
        stmt = stmt.order_by(Employee.first_name.asc(), Employee.last_name.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, employee: Employee) -> Employee:
        self.session.add(employee)
        await self.session.flush()
        return employee

    async def update(self, employee: Employee) -> Employee:
        employee.updated_at = datetime.now(UTC)
        employee.version += 1
        await self.session.flush()
        return employee

    async def soft_delete(self, employee: Employee) -> None:
        employee.is_deleted = True
        employee.deleted_at = datetime.now(UTC)
        employee.is_active = False
        employee.version += 1
        await self.session.flush()
