"""Payroll service."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.modules.hr.models.payroll import (
    EmployeeSalaryAssignment,
    PayrollRun,
    Payslip,
    PayslipLine,
    SalaryComponent,
    SalaryStructure,
    SalaryStructureItem,
)
from app.modules.hr.repositories.employee_repository import EmployeeRepository
from app.modules.hr.repositories.payroll_repository import PayrollRepository
from app.modules.hr.schemas.payroll import (
    EmployeeSalaryAssignmentCreate,
    PayrollRunApproveRequest,
    PayrollRunCreate,
    SalaryComponentCreate,
    SalaryStructureCreate,
)


class PayrollService:
    """Business service for Salary Components, Structures, Assignments, and Atomic Payroll Runs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.payroll_repo = PayrollRepository(session)
        self.emp_repo = EmployeeRepository(session)

    # --------------------------------------------------------------------------
    # Salary Components
    # --------------------------------------------------------------------------
    async def create_component(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: SalaryComponentCreate
    ) -> SalaryComponent:
        existing = await self.payroll_repo.get_component_by_code(data.code, tenant_id, org_id)
        if existing:
            raise ConflictException(f"Salary component with code '{data.code}' already exists")

        component = SalaryComponent(
            tenant_id=tenant_id,
            organization_id=org_id,
            code=data.code,
            name=data.name,
            component_type=data.component_type,
            calculation_type=data.calculation_type,
            is_taxable=data.is_taxable,
            formula_expression=data.formula_expression,
            is_active=data.is_active,
        )
        return await self.payroll_repo.create_component(component)

    async def list_components(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[SalaryComponent]:
        return await self.payroll_repo.list_components(tenant_id, org_id, is_active)

    # --------------------------------------------------------------------------
    # Salary Structures
    # --------------------------------------------------------------------------
    async def create_structure(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: SalaryStructureCreate
    ) -> tuple[SalaryStructure, Sequence[SalaryStructureItem]]:
        existing = await self.payroll_repo.get_structure_by_code(data.code, tenant_id, org_id)
        if existing:
            raise ConflictException(f"Salary structure with code '{data.code}' already exists")

        structure = SalaryStructure(
            tenant_id=tenant_id,
            organization_id=org_id,
            code=data.code,
            name=data.name,
            description=data.description,
            is_active=data.is_active,
        )

        items: list[SalaryStructureItem] = []
        for it in data.items:
            comp = await self.payroll_repo.get_component(it.component_id, tenant_id, org_id)
            if not comp:
                raise NotFoundException(f"Component '{it.component_id}' not found")
            items.append(
                SalaryStructureItem(
                    tenant_id=tenant_id,
                    organization_id=org_id,
                    component_id=it.component_id,
                    calculation_type=it.calculation_type,
                    amount_or_percentage=Decimal(str(it.amount_or_percentage)),
                    is_active=it.is_active,
                )
            )

        saved = await self.payroll_repo.create_structure(structure, items)
        saved_items = await self.payroll_repo.get_structure_items(saved.id, tenant_id, org_id)
        return saved, saved_items

    async def get_structure(
        self, structure_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> tuple[SalaryStructure, Sequence[SalaryStructureItem]]:
        structure = await self.payroll_repo.get_structure(structure_id, tenant_id, org_id)
        if not structure:
            raise NotFoundException(f"Salary structure '{structure_id}' not found")
        items = await self.payroll_repo.get_structure_items(structure.id, tenant_id, org_id)
        return structure, items

    async def list_structures(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[SalaryStructure]:
        return await self.payroll_repo.list_structures(tenant_id, org_id, is_active)

    # --------------------------------------------------------------------------
    # Salary Assignments
    # --------------------------------------------------------------------------
    async def create_assignment(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: EmployeeSalaryAssignmentCreate
    ) -> EmployeeSalaryAssignment:
        emp = await self.emp_repo.get_by_id(data.employee_id, tenant_id, org_id)
        if not emp:
            raise NotFoundException(f"Employee '{data.employee_id}' not found")

        structure = await self.payroll_repo.get_structure(
            data.salary_structure_id, tenant_id, org_id
        )
        if not structure:
            raise NotFoundException(f"Salary structure '{data.salary_structure_id}' not found")

        assignment = EmployeeSalaryAssignment(
            tenant_id=tenant_id,
            organization_id=org_id,
            employee_id=data.employee_id,
            salary_structure_id=data.salary_structure_id,
            base_gross_salary=Decimal(str(data.base_gross_salary)),
            currency=data.currency,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
            is_active=data.is_active,
        )
        return await self.payroll_repo.create_assignment(assignment)

    async def get_assignment_by_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> EmployeeSalaryAssignment | None:
        return await self.payroll_repo.get_assignment_by_employee(employee_id, tenant_id, org_id)

    # --------------------------------------------------------------------------
    # Payroll Runs & Processing
    # --------------------------------------------------------------------------
    async def create_payroll_run(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: PayrollRunCreate, user_id: uuid.UUID
    ) -> PayrollRun:
        if data.pay_period_end < data.pay_period_start:
            raise ValidationException("Pay period end date cannot be prior to start date")

        run_number = await self.payroll_repo.get_next_run_number(tenant_id, org_id)
        run = PayrollRun(
            tenant_id=tenant_id,
            organization_id=org_id,
            run_number=run_number,
            pay_period_start=data.pay_period_start,
            pay_period_end=data.pay_period_end,
            pay_date=data.pay_date,
            status="DRAFT",
            total_gross=Decimal("0.0"),
            total_deductions=Decimal("0.0"),
            total_net=Decimal("0.0"),
            total_employees=0,
            payment_method=data.payment_method,
            processed_by_id=user_id,
        )
        return await self.payroll_repo.create_payroll_run(run)

    async def process_payroll_run(
        self, run_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, user_id: uuid.UUID
    ) -> PayrollRun:
        run = await self.payroll_repo.get_payroll_run(run_id, tenant_id, org_id)
        if not run:
            raise NotFoundException(f"Payroll run '{run_id}' not found")
        if run.status not in ("DRAFT", "CALCULATED"):
            raise ValidationException(f"Cannot process payroll run in '{run.status}' state")

        assignments = await self.payroll_repo.list_active_assignments(tenant_id, org_id)
        if not assignments:
            raise ValidationException(
                "No active employee salary assignments found for payroll processing"
            )

        run_gross = Decimal("0.0")
        run_deductions = Decimal("0.0")
        run_net = Decimal("0.0")
        employee_count = 0

        for asgn in assignments:
            items = await self.payroll_repo.get_structure_items(
                asgn.salary_structure_id, tenant_id, org_id
            )
            base_gross = Decimal(str(asgn.base_gross_salary))

            basic_pay = Decimal("0.0")
            total_allowances = Decimal("0.0")
            total_emp_deductions = Decimal("0.0")
            payslip_lines: list[PayslipLine] = []

            # Process items on salary structure
            for item in items:
                comp = await self.payroll_repo.get_component(item.component_id, tenant_id, org_id)
                comp_name = comp.name if comp else "Salary Component"
                comp_type = comp.component_type if comp else "EARNING"
                is_taxable = comp.is_taxable if comp else True

                # Compute line amount
                if item.calculation_type == "PERCENTAGE":
                    line_amt = (base_gross * Decimal(str(item.amount_or_percentage))) / Decimal(
                        "100.0"
                    )
                else:
                    line_amt = Decimal(str(item.amount_or_percentage))

                if comp_type == "EARNING":
                    if comp and "basic" in comp.code.lower():
                        basic_pay += line_amt
                    else:
                        total_allowances += line_amt
                elif comp_type in ("DEDUCTION", "STATUTORY"):
                    total_emp_deductions += line_amt

                payslip_lines.append(
                    PayslipLine(
                        tenant_id=tenant_id,
                        organization_id=org_id,
                        component_id=item.component_id,
                        component_name=comp_name,
                        component_type=comp_type,
                        amount=line_amt,
                        is_taxable=is_taxable,
                    )
                )

            # If no items were defined on the structure, assign base_gross as basic_pay
            if not items:
                basic_pay = base_gross

            gross_pay = basic_pay + total_allowances
            net_pay = gross_pay - total_emp_deductions

            payslip_num = await self.payroll_repo.get_next_payslip_number(tenant_id, org_id)
            payslip = Payslip(
                tenant_id=tenant_id,
                organization_id=org_id,
                payroll_run_id=run.id,
                employee_id=asgn.employee_id,
                payslip_number=payslip_num,
                pay_period_start=run.pay_period_start,
                pay_period_end=run.pay_period_end,
                basic_pay=basic_pay,
                allowances=total_allowances,
                gross_pay=gross_pay,
                deductions=total_emp_deductions,
                net_pay=net_pay,
                total_worked_days=Decimal("30.0"),
                loss_of_pay_days=Decimal("0.0"),
                status="DRAFT",
            )
            self.session.add(payslip)
            await self.session.flush()

            for pline in payslip_lines:
                pline.payslip_id = payslip.id
                self.session.add(pline)

            run_gross += gross_pay
            run_deductions += total_emp_deductions
            run_net += net_pay
            employee_count += 1

        run.total_gross = run_gross
        run.total_deductions = run_deductions
        run.total_net = run_net
        run.total_employees = employee_count
        run.status = "CALCULATED"
        run.processed_by_id = user_id
        run.updated_at = datetime.now(UTC)

        return await self.payroll_repo.update_payroll_run(run)

    async def approve_payroll_run(
        self,
        run_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        data: PayrollRunApproveRequest,
    ) -> PayrollRun:
        run = await self.payroll_repo.get_payroll_run(run_id, tenant_id, org_id)
        if not run:
            raise NotFoundException(f"Payroll run '{run_id}' not found")
        if run.status != "CALCULATED":
            raise ValidationException(
                f"Only CALCULATED payroll runs can be approved (currently '{run.status}')"
            )

        run.status = data.status
        run.approved_by_id = user_id
        run.updated_at = datetime.now(UTC)
        return await self.payroll_repo.update_payroll_run(run)

    async def disburse_payroll_run(
        self, run_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, user_id: uuid.UUID
    ) -> PayrollRun:
        run = await self.payroll_repo.get_payroll_run(run_id, tenant_id, org_id)
        if not run:
            raise NotFoundException(f"Payroll run '{run_id}' not found")
        if run.status != "APPROVED":
            raise ValidationException(
                f"Only APPROVED payroll runs can be disbursed (currently '{run.status}')"
            )

        payslips = await self.payroll_repo.list_payslips_for_run(run.id, tenant_id, org_id)
        for ps in payslips:
            ps.status = "PAID"
            ps.transaction_reference = f"TXN-PAY-{ps.payslip_number}"

        run.status = "DISBURSED"
        run.updated_at = datetime.now(UTC)
        return await self.payroll_repo.update_payroll_run(run)

    async def get_payroll_run(
        self, run_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> PayrollRun:
        run = await self.payroll_repo.get_payroll_run(run_id, tenant_id, org_id)
        if not run:
            raise NotFoundException(f"Payroll run '{run_id}' not found")
        return run

    async def list_payroll_runs(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, status: str | None = None
    ) -> Sequence[PayrollRun]:
        return await self.payroll_repo.list_payroll_runs(tenant_id, org_id, status)

    async def get_payslip(
        self, payslip_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> tuple[Payslip, Sequence[PayslipLine]]:
        payslip = await self.payroll_repo.get_payslip(payslip_id, tenant_id, org_id)
        if not payslip:
            raise NotFoundException(f"Payslip '{payslip_id}' not found")
        lines = await self.payroll_repo.get_payslip_lines(payslip.id, tenant_id, org_id)
        return payslip, lines

    async def list_payslips_for_run(
        self, run_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[Payslip]:
        return await self.payroll_repo.list_payslips_for_run(run_id, tenant_id, org_id)

    async def list_payslips_for_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[Payslip]:
        return await self.payroll_repo.list_payslips_for_employee(employee_id, tenant_id, org_id)
