import uuid
from typing import Sequence
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.payroll_v7 import (
    EmployeeLoan,
    EmployeeSalaryAssignment,
    PayrollAdjustment,
    PayrollAuditLog,
    PayrollPeriod,
    PayrollRun,
    Payslip,
    PayslipItem,
    Reimbursement,
    SalaryComponent,
    SalaryStructure,
    SalaryStructureComponent,
)


class SalaryComponentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, component: SalaryComponent) -> SalaryComponent:
        self.db.add(component)
        await self.db.commit()
        await self.db.refresh(component)
        return component

    async def get_by_id(self, component_id: uuid.UUID) -> SalaryComponent | None:
        stmt = select(SalaryComponent).where(
            and_(SalaryComponent.id == component_id, SalaryComponent.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_code(self, org_id: uuid.UUID, code: str) -> SalaryComponent | None:
        stmt = select(SalaryComponent).where(
            and_(
                SalaryComponent.organization_id == org_id,
                SalaryComponent.code == code,
                SalaryComponent.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(self, org_id: uuid.UUID) -> Sequence[SalaryComponent]:
        stmt = (
            select(SalaryComponent)
            .where(and_(SalaryComponent.organization_id == org_id, SalaryComponent.is_deleted == False))
            .order_by(SalaryComponent.display_order.asc(), SalaryComponent.name.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, component: SalaryComponent) -> SalaryComponent:
        await self.db.commit()
        await self.db.refresh(component)
        return component

    async def delete(self, component_id: uuid.UUID) -> SalaryComponent | None:
        comp = await self.get_by_id(component_id)
        if comp:
            comp.is_deleted = True
            await self.db.commit()
        return comp


class SalaryStructureRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, structure: SalaryStructure) -> SalaryStructure:
        self.db.add(structure)
        await self.db.commit()
        await self.db.refresh(structure)
        return structure

    async def get_by_id(self, structure_id: uuid.UUID) -> SalaryStructure | None:
        stmt = (
            select(SalaryStructure)
            .options(selectinload(SalaryStructure.components))
            .where(and_(SalaryStructure.id == structure_id, SalaryStructure.is_deleted == False))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(self, org_id: uuid.UUID) -> Sequence[SalaryStructure]:
        stmt = (
            select(SalaryStructure)
            .options(selectinload(SalaryStructure.components))
            .where(and_(SalaryStructure.organization_id == org_id, SalaryStructure.is_deleted == False))
            .order_by(SalaryStructure.name.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, structure: SalaryStructure) -> SalaryStructure:
        await self.db.commit()
        await self.db.refresh(structure)
        return structure

    async def delete(self, structure_id: uuid.UUID) -> SalaryStructure | None:
        struct = await self.get_by_id(structure_id)
        if struct:
            struct.is_deleted = True
            await self.db.commit()
        return struct


class EmployeeSalaryAssignmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, assignment: EmployeeSalaryAssignment) -> EmployeeSalaryAssignment:
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    async def get_by_id(self, assignment_id: uuid.UUID) -> EmployeeSalaryAssignment | None:
        stmt = select(EmployeeSalaryAssignment).where(
            and_(EmployeeSalaryAssignment.id == assignment_id, EmployeeSalaryAssignment.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_active_by_employee(self, employee_id: uuid.UUID) -> EmployeeSalaryAssignment | None:
        stmt = (
            select(EmployeeSalaryAssignment)
            .options(
                selectinload(EmployeeSalaryAssignment.salary_structure).selectinload(
                    SalaryStructure.components
                ).selectinload(SalaryStructureComponent.salary_component)
            )
            .where(
                and_(
                    EmployeeSalaryAssignment.employee_id == employee_id,
                    EmployeeSalaryAssignment.status == "active",
                    EmployeeSalaryAssignment.is_deleted == False,
                )
            )
            .order_by(EmployeeSalaryAssignment.effective_from.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def list_by_employee(self, employee_id: uuid.UUID) -> Sequence[EmployeeSalaryAssignment]:
        stmt = (
            select(EmployeeSalaryAssignment)
            .where(and_(EmployeeSalaryAssignment.employee_id == employee_id, EmployeeSalaryAssignment.is_deleted == False))
            .order_by(EmployeeSalaryAssignment.effective_from.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def list_by_org(self, org_id: uuid.UUID) -> Sequence[EmployeeSalaryAssignment]:
        stmt = (
            select(EmployeeSalaryAssignment)
            .join(SalaryStructure)
            .where(
                and_(
                    SalaryStructure.organization_id == org_id,
                    EmployeeSalaryAssignment.is_deleted == False,
                )
            )
            .order_by(EmployeeSalaryAssignment.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, assignment: EmployeeSalaryAssignment) -> EmployeeSalaryAssignment:
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment


class PayrollPeriodRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, period: PayrollPeriod) -> PayrollPeriod:
        self.db.add(period)
        await self.db.commit()
        await self.db.refresh(period)
        return period

    async def get_by_id(self, period_id: uuid.UUID) -> PayrollPeriod | None:
        stmt = select(PayrollPeriod).where(
            and_(PayrollPeriod.id == period_id, PayrollPeriod.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_month_year(self, org_id: uuid.UUID, month: int, year: int) -> PayrollPeriod | None:
        stmt = select(PayrollPeriod).where(
            and_(
                PayrollPeriod.organization_id == org_id,
                PayrollPeriod.month == month,
                PayrollPeriod.year == year,
                PayrollPeriod.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(self, org_id: uuid.UUID) -> Sequence[PayrollPeriod]:
        stmt = (
            select(PayrollPeriod)
            .where(and_(PayrollPeriod.organization_id == org_id, PayrollPeriod.is_deleted == False))
            .order_by(PayrollPeriod.year.desc(), PayrollPeriod.month.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, period: PayrollPeriod) -> PayrollPeriod:
        await self.db.commit()
        await self.db.refresh(period)
        return period


class PayrollRunRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, run: PayrollRun) -> PayrollRun:
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def get_by_id(self, run_id: uuid.UUID) -> PayrollRun | None:
        stmt = (
            select(PayrollRun)
            .options(
                selectinload(PayrollRun.payslips).selectinload(Payslip.items),
                selectinload(PayrollRun.audit_logs),
            )
            .where(and_(PayrollRun.id == run_id, PayrollRun.is_deleted == False))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_period_id(self, period_id: uuid.UUID) -> PayrollRun | None:
        stmt = (
            select(PayrollRun)
            .options(
                selectinload(PayrollRun.payslips).selectinload(Payslip.items),
                selectinload(PayrollRun.audit_logs),
            )
            .where(and_(PayrollRun.payroll_period_id == period_id, PayrollRun.is_deleted == False))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(self, org_id: uuid.UUID) -> Sequence[PayrollRun]:
        stmt = (
            select(PayrollRun)
            .join(PayrollPeriod, PayrollRun.payroll_period_id == PayrollPeriod.id)
            .options(
                selectinload(PayrollRun.payslips).selectinload(Payslip.items),
                selectinload(PayrollRun.audit_logs),
            )
            .where(and_(PayrollPeriod.organization_id == org_id, PayrollRun.is_deleted == False))
            .order_by(PayrollRun.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, run: PayrollRun) -> PayrollRun:
        await self.db.commit()
        await self.db.refresh(run)
        return run


class PayslipRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payslip: Payslip) -> Payslip:
        self.db.add(payslip)
        await self.db.commit()
        await self.db.refresh(payslip)
        return payslip

    async def get_by_id(self, payslip_id: uuid.UUID) -> Payslip | None:
        stmt = (
            select(Payslip)
            .options(selectinload(Payslip.items))
            .where(and_(Payslip.id == payslip_id, Payslip.is_deleted == False))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_employee(self, employee_id: uuid.UUID) -> Sequence[Payslip]:
        stmt = (
            select(Payslip)
            .options(selectinload(Payslip.items))
            .where(and_(Payslip.employee_id == employee_id, Payslip.is_deleted == False))
            .order_by(Payslip.generated_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def list_by_run(self, run_id: uuid.UUID) -> Sequence[Payslip]:
        stmt = (
            select(Payslip)
            .options(selectinload(Payslip.items))
            .where(and_(Payslip.payroll_run_id == run_id, Payslip.is_deleted == False))
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()


class ReimbursementRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, reimbursement: Reimbursement) -> Reimbursement:
        self.db.add(reimbursement)
        await self.db.commit()
        await self.db.refresh(reimbursement)
        return reimbursement

    async def get_by_id(self, reimbursement_id: uuid.UUID) -> Reimbursement | None:
        stmt = select(Reimbursement).where(
            and_(Reimbursement.id == reimbursement_id, Reimbursement.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_employee(self, employee_id: uuid.UUID) -> Sequence[Reimbursement]:
        stmt = (
            select(Reimbursement)
            .where(and_(Reimbursement.employee_id == employee_id, Reimbursement.is_deleted == False))
            .order_by(Reimbursement.submitted_date.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def list_approved_pending_payout(self, employee_id: uuid.UUID) -> Sequence[Reimbursement]:
        stmt = select(Reimbursement).where(
            and_(
                Reimbursement.employee_id == employee_id,
                Reimbursement.status == "Approved",
                Reimbursement.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, reimbursement: Reimbursement) -> Reimbursement:
        await self.db.commit()
        await self.db.refresh(reimbursement)
        return reimbursement

    async def delete(self, reimbursement_id: uuid.UUID) -> Reimbursement | None:
        rem = await self.get_by_id(reimbursement_id)
        if rem:
            rem.is_deleted = True
            await self.db.commit()
        return rem


class EmployeeLoanRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, loan: EmployeeLoan) -> EmployeeLoan:
        self.db.add(loan)
        await self.db.commit()
        await self.db.refresh(loan)
        return loan

    async def get_by_id(self, loan_id: uuid.UUID) -> EmployeeLoan | None:
        stmt = select(EmployeeLoan).where(
            and_(EmployeeLoan.id == loan_id, EmployeeLoan.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_active_by_employee(self, employee_id: uuid.UUID) -> Sequence[EmployeeLoan]:
        stmt = select(EmployeeLoan).where(
            and_(
                EmployeeLoan.employee_id == employee_id,
                EmployeeLoan.status == "Active",
                EmployeeLoan.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def list_by_employee(self, employee_id: uuid.UUID) -> Sequence[EmployeeLoan]:
        stmt = (
            select(EmployeeLoan)
            .where(and_(EmployeeLoan.employee_id == employee_id, EmployeeLoan.is_deleted == False))
            .order_by(EmployeeLoan.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, loan: EmployeeLoan) -> EmployeeLoan:
        await self.db.commit()
        await self.db.refresh(loan)
        return loan

    async def delete(self, loan_id: uuid.UUID) -> EmployeeLoan | None:
        loan = await self.get_by_id(loan_id)
        if loan:
            loan.is_deleted = True
            await self.db.commit()
        return loan


class PayrollAdjustmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, adjustment: PayrollAdjustment) -> PayrollAdjustment:
        self.db.add(adjustment)
        await self.db.commit()
        await self.db.refresh(adjustment)
        return adjustment

    async def list_by_employee_and_period(
        self, employee_id: uuid.UUID, period_id: uuid.UUID
    ) -> Sequence[PayrollAdjustment]:
        stmt = select(PayrollAdjustment).where(
            and_(
                PayrollAdjustment.employee_id == employee_id,
                PayrollAdjustment.payroll_period_id == period_id,
                PayrollAdjustment.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()


class PayrollAuditLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, log: PayrollAuditLog) -> PayrollAuditLog:
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log


# Backward compatibility aliases
SalaryAssignmentRepository = EmployeeSalaryAssignmentRepository
LoanRepository = EmployeeLoanRepository
