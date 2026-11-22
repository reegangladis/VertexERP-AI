"""Employee service."""

import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.modules.hr.models.employee import Employee
from app.modules.hr.repositories.employee_repository import EmployeeRepository
from app.modules.hr.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    """Business service for Employee domain operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.employee_repo = EmployeeRepository(session)

    async def create_employee(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: EmployeeCreate
    ) -> Employee:
        # Check duplicate email in organization
        existing_email = await self.employee_repo.get_by_email(data.email, tenant_id, org_id)
        if existing_email:
            raise ConflictException(f"Employee with email '{data.email}' already exists")

        # Auto-generate employee_number if not supplied
        employee_number = data.employee_number
        if not employee_number:
            count = await self.employee_repo.count_by_org(tenant_id, org_id)
            employee_number = f"EMP-{count + 1:04d}"
        else:
            existing_num = await self.employee_repo.get_by_number(
                employee_number, tenant_id, org_id
            )
            if existing_num:
                raise ConflictException(f"Employee with number '{employee_number}' already exists")

        # Validate reporting manager if specified
        if data.reporting_manager_id:
            manager = await self.employee_repo.get_by_id(
                data.reporting_manager_id, tenant_id, org_id
            )
            if not manager:
                raise NotFoundException(
                    f"Reporting manager '{data.reporting_manager_id}' not found"
                )

        employee = Employee(
            tenant_id=tenant_id,
            organization_id=org_id,
            user_id=data.user_id,
            employee_number=employee_number,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email.lower(),
            phone=data.phone,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            hire_date=data.hire_date,
            employment_status=data.employment_status,
            department_id=data.department_id,
            branch_id=data.branch_id,
            designation_id=data.designation_id,
            reporting_manager_id=data.reporting_manager_id,
            is_active=data.is_active,
        )
        return await self.employee_repo.create(employee)

    async def get_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Employee:
        employee = await self.employee_repo.get_by_id(employee_id, tenant_id, org_id)
        if not employee:
            raise NotFoundException(f"Employee '{employee_id}' not found")
        return employee

    async def list_employees(
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
        return await self.employee_repo.list_by_org(
            tenant_id=tenant_id,
            org_id=org_id,
            department_id=department_id,
            branch_id=branch_id,
            designation_id=designation_id,
            status=status,
            is_active=is_active,
            search=search,
        )

    async def update_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, data: EmployeeUpdate
    ) -> Employee:
        employee = await self.get_employee(employee_id, tenant_id, org_id)

        if data.email is not None and data.email.lower() != employee.email:
            existing = await self.employee_repo.get_by_email(data.email, tenant_id, org_id)
            if existing and existing.id != employee.id:
                raise ConflictException(f"Employee with email '{data.email}' already exists")
            employee.email = data.email.lower()

        if data.reporting_manager_id is not None:
            if data.reporting_manager_id == employee.id:
                raise ValidationException("An employee cannot report to themselves")
            manager = await self.employee_repo.get_by_id(
                data.reporting_manager_id, tenant_id, org_id
            )
            if not manager:
                raise NotFoundException(
                    f"Reporting manager '{data.reporting_manager_id}' not found"
                )
            employee.reporting_manager_id = data.reporting_manager_id

        if data.first_name is not None:
            employee.first_name = data.first_name
        if data.last_name is not None:
            employee.last_name = data.last_name
        if data.phone is not None:
            employee.phone = data.phone
        if data.date_of_birth is not None:
            employee.date_of_birth = data.date_of_birth
        if data.gender is not None:
            employee.gender = data.gender
        if data.hire_date is not None:
            employee.hire_date = data.hire_date
        if data.employment_status is not None:
            employee.employment_status = data.employment_status
        if data.department_id is not None:
            employee.department_id = data.department_id
        if data.branch_id is not None:
            employee.branch_id = data.branch_id
        if data.designation_id is not None:
            employee.designation_id = data.designation_id
        if data.user_id is not None:
            employee.user_id = data.user_id
        if data.is_active is not None:
            employee.is_active = data.is_active

        return await self.employee_repo.update(employee)

    async def delete_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> None:
        employee = await self.get_employee(employee_id, tenant_id, org_id)
        await self.employee_repo.soft_delete(employee)
