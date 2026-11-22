"""Payroll repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hr.models.payroll import (
    EmployeeSalaryAssignment,
    PayrollRun,
    Payslip,
    PayslipLine,
    SalaryComponent,
    SalaryStructure,
    SalaryStructureItem,
)


class PayrollRepository:
    """PostgreSQL implementation of Payroll repository with multi-tenant filtering."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # --------------------------------------------------------------------------
    # Salary Components
    # --------------------------------------------------------------------------
    async def create_component(self, component: SalaryComponent) -> SalaryComponent:
        self.session.add(component)
        await self.session.commit()
        await self.session.refresh(component)
        return component

    async def get_component(
        self, component_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> SalaryComponent | None:
        stmt = select(SalaryComponent).where(
            SalaryComponent.id == component_id,
            SalaryComponent.tenant_id == tenant_id,
            SalaryComponent.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_component_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> SalaryComponent | None:
        stmt = select(SalaryComponent).where(
            SalaryComponent.code == code,
            SalaryComponent.tenant_id == tenant_id,
            SalaryComponent.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_components(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[SalaryComponent]:
        stmt = select(SalaryComponent).where(
            SalaryComponent.tenant_id == tenant_id,
            SalaryComponent.organization_id == org_id,
        )
        if is_active is not None:
            stmt = stmt.where(SalaryComponent.is_active == is_active)
        stmt = stmt.order_by(SalaryComponent.name.asc())
        res = await self.session.execute(stmt)
        return res.scalars().all()

    # --------------------------------------------------------------------------
    # Salary Structures
    # --------------------------------------------------------------------------
    async def create_structure(
        self, structure: SalaryStructure, items: list[SalaryStructureItem]
    ) -> SalaryStructure:
        self.session.add(structure)
        await self.session.flush()

        for item in items:
            item.salary_structure_id = structure.id
            self.session.add(item)

        await self.session.commit()
        await self.session.refresh(structure)
        return structure

    async def get_structure(
        self, structure_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> SalaryStructure | None:
        stmt = select(SalaryStructure).where(
            SalaryStructure.id == structure_id,
            SalaryStructure.tenant_id == tenant_id,
            SalaryStructure.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_structure_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> SalaryStructure | None:
        stmt = select(SalaryStructure).where(
            SalaryStructure.code == code,
            SalaryStructure.tenant_id == tenant_id,
            SalaryStructure.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_structure_items(
        self, structure_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[SalaryStructureItem]:
        stmt = select(SalaryStructureItem).where(
            SalaryStructureItem.salary_structure_id == structure_id,
            SalaryStructureItem.tenant_id == tenant_id,
            SalaryStructureItem.organization_id == org_id,
            SalaryStructureItem.is_active.is_(True),
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def list_structures(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[SalaryStructure]:
        stmt = select(SalaryStructure).where(
            SalaryStructure.tenant_id == tenant_id,
            SalaryStructure.organization_id == org_id,
        )
        if is_active is not None:
            stmt = stmt.where(SalaryStructure.is_active == is_active)
        stmt = stmt.order_by(SalaryStructure.name.asc())
        res = await self.session.execute(stmt)
        return res.scalars().all()

    # --------------------------------------------------------------------------
    # Salary Assignments
    # --------------------------------------------------------------------------
    async def create_assignment(
        self, assignment: EmployeeSalaryAssignment
    ) -> EmployeeSalaryAssignment:
        self.session.add(assignment)
        await self.session.commit()
        await self.session.refresh(assignment)
        return assignment

    async def get_assignment_by_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> EmployeeSalaryAssignment | None:
        stmt = (
            select(EmployeeSalaryAssignment)
            .where(
                EmployeeSalaryAssignment.employee_id == employee_id,
                EmployeeSalaryAssignment.tenant_id == tenant_id,
                EmployeeSalaryAssignment.organization_id == org_id,
                EmployeeSalaryAssignment.is_active.is_(True),
            )
            .order_by(EmployeeSalaryAssignment.effective_from.desc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_active_assignments(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmployeeSalaryAssignment]:
        stmt = select(EmployeeSalaryAssignment).where(
            EmployeeSalaryAssignment.tenant_id == tenant_id,
            EmployeeSalaryAssignment.organization_id == org_id,
            EmployeeSalaryAssignment.is_active.is_(True),
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    # --------------------------------------------------------------------------
    # Payroll Runs
    # --------------------------------------------------------------------------
    async def get_next_run_number(self, tenant_id: uuid.UUID, org_id: uuid.UUID) -> str:
        stmt = select(func.count(PayrollRun.id)).where(
            PayrollRun.tenant_id == tenant_id,
            PayrollRun.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        count = res.scalar() or 0
        return f"PR-{count + 1:04d}"

    async def create_payroll_run(self, run: PayrollRun) -> PayrollRun:
        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def get_payroll_run(
        self, run_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> PayrollRun | None:
        stmt = select(PayrollRun).where(
            PayrollRun.id == run_id,
            PayrollRun.tenant_id == tenant_id,
            PayrollRun.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_payroll_run(self, run: PayrollRun) -> PayrollRun:
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def list_payroll_runs(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, status: str | None = None
    ) -> Sequence[PayrollRun]:
        stmt = select(PayrollRun).where(
            PayrollRun.tenant_id == tenant_id,
            PayrollRun.organization_id == org_id,
        )
        if status:
            stmt = stmt.where(PayrollRun.status == status)
        stmt = stmt.order_by(PayrollRun.created_at.desc())
        res = await self.session.execute(stmt)
        return res.scalars().all()

    # --------------------------------------------------------------------------
    # Payslips & Lines
    # --------------------------------------------------------------------------
    async def get_next_payslip_number(self, tenant_id: uuid.UUID, org_id: uuid.UUID) -> str:
        stmt = select(func.count(Payslip.id)).where(
            Payslip.tenant_id == tenant_id,
            Payslip.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        count = res.scalar() or 0
        return f"PS-{count + 1:06d}"

    async def get_payslip(
        self, payslip_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Payslip | None:
        stmt = select(Payslip).where(
            Payslip.id == payslip_id,
            Payslip.tenant_id == tenant_id,
            Payslip.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_payslip_lines(
        self, payslip_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[PayslipLine]:
        stmt = (
            select(PayslipLine)
            .where(
                PayslipLine.payslip_id == payslip_id,
                PayslipLine.tenant_id == tenant_id,
                PayslipLine.organization_id == org_id,
            )
            .order_by(PayslipLine.component_type.asc(), PayslipLine.created_at.asc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def list_payslips_for_run(
        self, payroll_run_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[Payslip]:
        stmt = (
            select(Payslip)
            .where(
                Payslip.payroll_run_id == payroll_run_id,
                Payslip.tenant_id == tenant_id,
                Payslip.organization_id == org_id,
            )
            .order_by(Payslip.payslip_number.asc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def list_payslips_for_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[Payslip]:
        stmt = (
            select(Payslip)
            .where(
                Payslip.employee_id == employee_id,
                Payslip.tenant_id == tenant_id,
                Payslip.organization_id == org_id,
            )
            .order_by(Payslip.pay_period_start.desc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
