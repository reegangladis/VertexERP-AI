import csv
import io
import os
import uuid
from datetime import date, datetime, time
from typing import Any

from fastapi import UploadFile
from sqlalchemy import select

from app.models.attendance import Attendance
from app.models.employee import (
    Employee,
    EmployeeDocument,
)
from app.models.leave import LeaveBalance, LeaveRequest
from app.models.payroll import SalaryStructure
from app.repositories.hr_mgmt import (
    AttendanceRepository,
    EmployeeDocumentRepository,
    EmployeeProfileRepository,
    EmployeeRepository,
    LeaveBalanceRepository,
    LeaveRequestRepository,
    LeaveTypeRepository,
    SalaryStructureRepository,
)
from app.services.base import BaseService


class HRServiceException(Exception):
    pass


class EmployeeService(BaseService[Employee, EmployeeRepository]):
    def __init__(
        self, repository: EmployeeRepository, profile_repo: EmployeeProfileRepository
    ):
        super().__init__(repository)
        self.profile_repo = profile_repo

    async def create_employee(
        self, org_id: uuid.UUID, data: dict[str, Any]
    ) -> Employee:
        # Check code duplicate
        existing = await self.repository.get_code(org_id, data.get("employee_code"))
        if existing:
            raise HRServiceException(
                f"Employee code {data.get('employee_code')} already registered."
            )

        profile_data = data.pop("profile", None)
        emp_data = {"organization_id": org_id, **data}
        employee = await self.repository.create(emp_data)

        if profile_data:
            await self.profile_repo.create({"employee_id": employee.id, **profile_data})
        return employee

    async def update_employee(
        self, emp_id: uuid.UUID, data: dict[str, Any]
    ) -> Employee:
        employee = await self.repository.get(emp_id)
        if not employee:
            raise HRServiceException("Employee not found.")

        profile_data = data.pop("profile", None)
        employee = await self.repository.update(employee, data)

        if profile_data and employee.profile:
            await self.profile_repo.update(employee.profile, profile_data)
        elif profile_data:
            await self.profile_repo.create({"employee_id": employee.id, **profile_data})
        return employee

    async def bulk_import_csv(self, org_id: uuid.UUID, file_content: bytes) -> int:
        stream = io.StringIO(file_content.decode("utf-8"))
        reader = csv.DictReader(stream)
        count = 0
        for row in reader:
            # Simple format verification and creation
            code = row.get("employee_code")
            if not code:
                continue

            existing = await self.repository.get_code(org_id, code)
            if existing:
                continue  # Skip duplicates in bulk import

            emp_dict = {
                "employee_code": code,
                "employment_type": row.get("employment_type", "full-time"),
                "status": row.get("status", "active"),
                "date_joined": date.fromisoformat(
                    row.get("date_joined", date.today().isoformat())
                ),
            }

            # optional profile details
            profile_dict = {
                "personal_email": row.get("personal_email"),
                "personal_phone": row.get("personal_phone"),
                "nationality": row.get("nationality"),
            }

            emp = await self.repository.create({"organization_id": org_id, **emp_dict})
            await self.profile_repo.create({"employee_id": emp.id, **profile_dict})
            count += 1
        return count


class AttendanceService(BaseService[Attendance, AttendanceRepository]):
    def __init__(self, repository: AttendanceRepository):
        super().__init__(repository)

    async def check_in(
        self, employee_id: uuid.UUID, check_in_time: datetime
    ) -> Attendance:
        today = check_in_time.date()

        # Check if already has punch card today
        stmt = select(Attendance).where(
            Attendance.employee_id == employee_id,
            Attendance.date == today,
            Attendance.is_deleted == False,
        )
        res = await self.repository.db.execute(stmt)
        attendance = res.scalar_one_or_none()

        # Shift threshold (late after 09:15 AM)
        shift_threshold = time(9, 15)
        is_late = check_in_time.time() > shift_threshold

        if attendance:
            # If already checked in
            if attendance.check_in:
                raise HRServiceException("Employee already checked in today.")
            attendance.check_in = check_in_time
            attendance.status = "present"
            attendance.is_late_arrival = is_late
            return await self.repository.update(attendance, {})

        # Create new attendance record
        return await self.repository.create(
            {
                "employee_id": employee_id,
                "date": today,
                "check_in": check_in_time,
                "status": "present",
                "is_late_arrival": is_late,
            }
        )

    async def check_out(
        self, employee_id: uuid.UUID, check_out_time: datetime
    ) -> Attendance:
        today = check_out_time.date()

        stmt = select(Attendance).where(
            Attendance.employee_id == employee_id,
            Attendance.date == today,
            Attendance.is_deleted == False,
        )
        res = await self.repository.db.execute(stmt)
        attendance = res.scalar_one_or_none()

        if not attendance or not attendance.check_in:
            raise HRServiceException("Active check-in card not found for today.")

        attendance.check_out = check_out_time

        # Calculate working hours
        delta = check_out_time - attendance.check_in
        hours = delta.total_seconds() / 3600.0

        # Deduct breaks if break tracking completed
        break_mins = attendance.total_break_minutes or 0
        hours = max(0.0, hours - (break_mins / 60.0))
        attendance.total_hours = round(hours, 2)

        # Early exit check (before 05:00 PM)
        exit_threshold = time(17, 0)
        attendance.is_early_exit = check_out_time.time() < exit_threshold

        # Overtime calculation (hours beyond 8.0 standard shift)
        if hours > 8.0:
            overtime_hrs = hours - 8.0
            attendance.overtime_minutes = int(overtime_hrs * 60)

        return await self.repository.update(attendance, {})


class LeaveService(BaseService[LeaveRequest, LeaveRequestRepository]):
    def __init__(
        self,
        repository: LeaveRequestRepository,
        balance_repo: LeaveBalanceRepository,
        type_repo: LeaveTypeRepository,
    ):
        super().__init__(repository)
        self.balance_repo = balance_repo
        self.type_repo = type_repo

    async def submit_request(
        self, org_id: uuid.UUID, data: dict[str, Any]
    ) -> LeaveRequest:
        employee_id = data.get("employee_id")
        leave_type_id = data.get("leave_type_id")
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        # Total days count
        delta = end_date - start_date
        total_days = delta.days + 1
        if total_days <= 0:
            raise HRServiceException("End date must be after start date.")

        # Check balance
        stmt = select(LeaveBalance).where(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.leave_type_id == leave_type_id,
            LeaveBalance.is_deleted == False,
        )
        res = await self.balance_repo.db.execute(stmt)
        balance = res.scalar_one_or_none()

        if not balance or balance.remaining < total_days:
            raise HRServiceException(
                f"Insufficient leave balance. Required: {total_days}, Available: {balance.remaining if balance else 0.0}"
            )

        # Create leave request
        return await self.repository.create(
            {**data, "total_days": total_days, "status": "pending"}
        )

    async def process_approval(
        self,
        request_id: uuid.UUID,
        approver_id: uuid.UUID,
        status: str,
        comment: str | None,
    ) -> LeaveRequest:
        request = await self.repository.get(request_id)
        if not request:
            raise HRServiceException("Leave request not found.")
        if request.status != "pending":
            raise HRServiceException("Leave request already processed.")

        if status == "approved":
            # Subtract balance
            stmt = select(LeaveBalance).where(
                LeaveBalance.employee_id == request.employee_id,
                LeaveBalance.leave_type_id == request.leave_type_id,
                LeaveBalance.is_deleted == False,
            )
            res = await self.balance_repo.db.execute(stmt)
            balance = res.scalar_one_or_none()
            if balance:
                balance.used += request.total_days
                balance.remaining -= request.total_days
                await self.balance_repo.update(balance, {})

        request.status = status
        request.approved_by_id = approver_id
        request.approval_comment = comment
        return await self.repository.update(request, {})


class DocumentUploadService(BaseService[EmployeeDocument, EmployeeDocumentRepository]):
    def __init__(self, repository: EmployeeDocumentRepository):
        super().__init__(repository)
        self.upload_dir = "uploads/hr"
        os.makedirs(self.upload_dir, exist_ok=True)

    async def upload_document(
        self,
        employee_id: uuid.UUID,
        name: str,
        doc_type: str,
        file: UploadFile,
        provider: str = "local",
    ) -> EmployeeDocument:
        content = await file.read()
        file_size = len(content)
        mime_type = file.content_type

        file_path = ""
        if provider == "local":
            filename = f"{uuid.uuid4()}_{file.filename}"
            full_path = os.path.join(self.upload_dir, filename)
            with open(full_path, "wb") as f:
                f.write(content)
            file_path = f"uploads/hr/{filename}"
        else:
            file_path = f"mock://{provider}-bucket/{uuid.uuid4()}_{file.filename}"

        return await self.repository.create(
            {
                "employee_id": employee_id,
                "name": name,
                "type": doc_type,
                "file_path": file_path,
                "file_size": file_size,
                "mime_type": mime_type,
                "storage_provider": provider,
            }
        )


from app.models.payroll import PayrollRun, Payslip
from app.repositories.hr_mgmt import PayrollRunRepository, PayslipRepository


class PayrollService(BaseService[PayrollRun, PayrollRunRepository]):
    def __init__(
        self,
        repository: PayrollRunRepository,
        payslip_repo: PayslipRepository,
        salary_repo: SalaryStructureRepository,
        employee_repo: EmployeeRepository,
    ):
        super().__init__(repository)
        self.payslip_repo = payslip_repo
        self.salary_repo = salary_repo
        self.employee_repo = employee_repo

    async def process_payroll(
        self, org_id: uuid.UUID, month: int, year: int
    ) -> PayrollRun:
        existing = await self.repository.get_by_period(org_id, month, year)
        if existing and existing.status == "paid":
            raise HRServiceException(
                f"Payroll for {month}/{year} is already finalized and paid."
            )

        if not existing:
            payroll_run = await self.repository.create(
                {
                    "organization_id": org_id,
                    "period_month": month,
                    "period_year": year,
                    "status": "processing",
                    "total_gross": 0.0,
                    "total_deductions": 0.0,
                    "total_net": 0.0,
                }
            )
        else:
            payroll_run = existing
            payroll_run.status = "processing"

        employees = await self.employee_repo.get_by_org(org_id)
        active_employees = [e for e in employees if e.status == "active"]

        total_gross = 0.0
        total_deductions = 0.0
        total_net = 0.0

        for emp in active_employees:
            stmt = select(SalaryStructure).where(
                SalaryStructure.employee_id == emp.id,
                SalaryStructure.is_deleted == False,
            )
            res = await self.repository.db.execute(stmt)
            struct = res.scalars().first()

            base_salary = float(struct.base_salary) if struct else 5000.0
            allowances_dict = (
                struct.allowances
                if (struct and isinstance(struct.allowances, dict))
                else {"housing": 1000.0, "transport": 500.0}
            )
            deductions_dict = (
                struct.deductions
                if (struct and isinstance(struct.deductions, dict))
                else {"tax": base_salary * 0.1, "insurance": 200.0}
            )

            total_allow = sum(float(v) for v in allowances_dict.values())
            total_deduct = sum(float(v) for v in deductions_dict.values())
            net = (base_salary + total_allow) - total_deduct

            total_gross += base_salary + total_allow
            total_deductions += total_deduct
            total_net += net

            stmt_ps = select(Payslip).where(
                Payslip.payroll_run_id == payroll_run.id,
                Payslip.employee_id == emp.id,
                Payslip.is_deleted == False,
            )
            res_ps = await self.repository.db.execute(stmt_ps)
            ps_existing = res_ps.scalar_one_or_none()

            ps_data = {
                "payroll_run_id": payroll_run.id,
                "employee_id": emp.id,
                "base_salary": base_salary,
                "total_allowances": total_allow,
                "total_deductions": total_deduct,
                "net_salary": net,
                "allowances_breakdown": allowances_dict,
                "deductions_breakdown": deductions_dict,
                "status": "generated",
            }

            if ps_existing:
                await self.payslip_repo.update(ps_existing, ps_data)
            else:
                await self.payslip_repo.create(ps_data)

        payroll_run.status = "approved"
        payroll_run.total_gross = total_gross
        payroll_run.total_deductions = total_deductions
        payroll_run.total_net = total_net
        payroll_run.processed_at = datetime.now()

        return await self.repository.update(payroll_run, {})


# Add model utilities to repository subclass
EmployeeRepository.get_code = (
    EmployeeRepository.get_code
    if hasattr(EmployeeRepository, "get_code")
    else lambda self, org_id, code: self.get_by_code(org_id, code)
)
