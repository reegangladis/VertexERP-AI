import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.modules.hr.models.leave import (
    LeaveBalance,
    LeavePolicy,
    LeaveRequest,
    LeaveType,
)
from app.modules.hr.repositories.employee_repository import EmployeeRepository
from app.modules.hr.repositories.leave_repository import LeaveRepository
from app.modules.hr.schemas.leave import (
    LeaveApprovalRequest,
    LeavePolicyCreate,
    LeaveRequestCreate,
    LeaveTypeCreate,
)


class LeaveService:
    """Business service for Leave Types, Policies, Balances, and Approvals."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.leave_repo = LeaveRepository(session)
        self.emp_repo = EmployeeRepository(session)

    async def _ensure_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> None:
        emp = await self.emp_repo.get_by_id(employee_id, tenant_id, org_id)
        if not emp:
            raise NotFoundException(f"Employee '{employee_id}' not found")

    # Leave Types
    async def create_type(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: LeaveTypeCreate
    ) -> LeaveType:
        existing = await self.leave_repo.get_type_by_code(data.code, tenant_id, org_id)
        if existing:
            raise ConflictException(f"Leave type with code '{data.code}' already exists")
        leave_type = LeaveType(
            tenant_id=tenant_id,
            organization_id=org_id,
            code=data.code,
            name=data.name,
            description=data.description,
            is_paid=data.is_paid,
            is_encashable=data.is_encashable,
            max_consecutive_days=data.max_consecutive_days,
            color_code=data.color_code,
            is_active=data.is_active,
        )
        return await self.leave_repo.create_type(leave_type)

    async def list_types(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[LeaveType]:
        return await self.leave_repo.list_types(tenant_id, org_id, is_active)

    # Policies
    async def create_policy(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: LeavePolicyCreate
    ) -> LeavePolicy:
        leave_type = await self.leave_repo.get_type(data.leave_type_id, tenant_id, org_id)
        if not leave_type:
            raise NotFoundException(f"Leave type '{data.leave_type_id}' not found")

        policy = LeavePolicy(
            tenant_id=tenant_id,
            organization_id=org_id,
            leave_type_id=data.leave_type_id,
            annual_allocation_days=Decimal(str(data.annual_allocation_days)),
            accrual_frequency=data.accrual_frequency,
            carry_forward_max_days=Decimal(str(data.carry_forward_max_days)),
            probation_allowed=data.probation_allowed,
            is_active=data.is_active,
        )
        return await self.leave_repo.create_policy(policy)

    # Balances
    async def get_or_create_balance(
        self,
        employee_id: uuid.UUID,
        leave_type_id: uuid.UUID,
        fiscal_year: int,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> LeaveBalance:
        await self._ensure_employee(employee_id, tenant_id, org_id)
        balance = await self.leave_repo.get_balance(
            employee_id, leave_type_id, fiscal_year, tenant_id, org_id
        )
        if not balance:
            policy = await self.leave_repo.get_policy(leave_type_id, tenant_id, org_id)
            allocated = Decimal(str(policy.annual_allocation_days)) if policy else Decimal("12.0")
            balance = LeaveBalance(
                tenant_id=tenant_id,
                organization_id=org_id,
                employee_id=employee_id,
                leave_type_id=leave_type_id,
                fiscal_year=fiscal_year,
                allocated_days=allocated,
                used_days=Decimal("0.0"),
                pending_days=Decimal("0.0"),
                carry_forward_days=Decimal("0.0"),
                balance_days=allocated,
            )
            balance = await self.leave_repo.create_balance(balance)
        return balance

    async def list_balances(
        self, employee_id: uuid.UUID, fiscal_year: int, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[LeaveBalance]:
        await self._ensure_employee(employee_id, tenant_id, org_id)
        return await self.leave_repo.list_balances_for_employee(
            employee_id, fiscal_year, tenant_id, org_id
        )

    # Requests
    async def submit_request(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: LeaveRequestCreate
    ) -> LeaveRequest:
        await self._ensure_employee(data.employee_id, tenant_id, org_id)
        leave_type = await self.leave_repo.get_type(data.leave_type_id, tenant_id, org_id)
        if not leave_type:
            raise NotFoundException(f"Leave type '{data.leave_type_id}' not found")

        if data.end_date < data.start_date:
            raise ValidationException("End date cannot be prior to start date")

        # Check balance
        fiscal_year = data.start_date.year
        balance = await self.get_or_create_balance(
            data.employee_id, data.leave_type_id, fiscal_year, tenant_id, org_id
        )
        req_days = Decimal(str(data.total_days))
        available = Decimal(str(balance.balance_days)) - Decimal(str(balance.pending_days))
        if req_days > available:
            raise ValidationException(
                f"Insufficient leave balance. Available: {available}, Requested: {data.total_days}"
            )

        # Update pending
        balance.pending_days = Decimal(str(balance.pending_days)) + req_days
        await self.leave_repo.update_balance(balance)

        req = LeaveRequest(
            tenant_id=tenant_id,
            organization_id=org_id,
            employee_id=data.employee_id,
            leave_type_id=data.leave_type_id,
            start_date=data.start_date,
            end_date=data.end_date,
            total_days=req_days,
            reason=data.reason,
            status="SUBMITTED",
        )
        return await self.leave_repo.create_request(req)

    async def review_request(
        self,
        request_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        data: LeaveApprovalRequest,
    ) -> LeaveRequest:
        req = await self.leave_repo.get_request(request_id, tenant_id, org_id)
        if not req:
            raise NotFoundException(f"Leave request '{request_id}' not found")
        if req.status not in ("SUBMITTED", "DRAFT"):
            raise ValidationException(f"Cannot review leave request in '{req.status}' state")

        fiscal_year = req.start_date.year
        balance = await self.get_or_create_balance(
            req.employee_id, req.leave_type_id, fiscal_year, tenant_id, org_id
        )

        req.status = data.status
        req.approver_id = user_id
        req.approved_at = datetime.now(UTC)
        req.remarks = data.remarks

        total_days = Decimal(str(req.total_days))
        pending_days = Decimal(str(balance.pending_days))
        used_days = Decimal(str(balance.used_days))
        balance_days = Decimal(str(balance.balance_days))

        if data.status == "APPROVED":
            balance.pending_days = max(Decimal("0.0"), pending_days - total_days)
            balance.used_days = used_days + total_days
            balance.balance_days = max(Decimal("0.0"), balance_days - total_days)
        elif data.status == "REJECTED":
            balance.pending_days = max(Decimal("0.0"), pending_days - total_days)

        await self.leave_repo.update_balance(balance)
        return await self.leave_repo.update_request(req)

    async def list_requests(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        employee_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> Sequence[LeaveRequest]:
        return await self.leave_repo.list_requests(tenant_id, org_id, employee_id, status)
