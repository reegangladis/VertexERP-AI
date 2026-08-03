import uuid
from datetime import UTC, date, datetime, timedelta

from fastapi import HTTPException, status

from app.models.leave_v6 import (
    CompOff,
    HolidayCalendar,
    HolidayEvent,
    LeaveAccrual,
    LeaveApproval,
    LeaveBalance,
    LeavePolicy,
    LeavePolicyAssignment,
    LeaveRequest,
    LeaveType,
)
from app.repositories.leave import (
    CompOffRepository,
    HolidayCalendarRepository,
    LeaveAccrualRepository,
    LeaveApprovalRepository,
    LeaveBalanceRepository,
    LeavePolicyRepository,
    LeaveRequestRepository,
    LeaveTypeRepository,
)
from app.schemas.leave import (
    CompOffCreate,
    CompOffResponse,
    HolidayCalendarCreate,
    HolidayCalendarResponse,
    HolidayEventCreate,
    HolidayEventResponse,
    LeaveAccrualResponse,
    LeaveBalanceResponse,
    LeaveBalanceUpdate,
    LeaveDashboardSummary,
    LeavePolicyAssignmentCreate,
    LeavePolicyAssignmentResponse,
    LeavePolicyCreate,
    LeavePolicyResponse,
    LeavePolicyUpdate,
    LeaveApprovalResponse,
    LeaveApprovalRequest,
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveTypeCreate,
    LeaveTypeResponse,
    LeaveTypeUpdate,
)


class LeaveService:
    def __init__(self, db_session):
        self.db = db_session
        self.type_repo = LeaveTypeRepository(db_session)
        self.policy_repo = LeavePolicyRepository(db_session)
        self.balance_repo = LeaveBalanceRepository(db_session)
        self.request_repo = LeaveRequestRepository(db_session)
        self.approval_repo = LeaveApprovalRepository(db_session)
        self.accrual_repo = LeaveAccrualRepository(db_session)
        self.compoff_repo = CompOffRepository(db_session)
        self.holiday_repo = HolidayCalendarRepository(db_session)

    # --- Net Working Days Calculation ---
    async def calculate_net_days(
        self, org_id: uuid.UUID, start_date: date, end_date: date, is_half_day: bool = False
    ) -> float:
        if is_half_day:
            return 0.5

        if end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date cannot be prior to start date.",
            )

        holidays = await self.holiday_repo.list_events_between(org_id, start_date, end_date)
        holiday_dates = {h.holiday_date for h in holidays if not h.is_optional}

        count = 0.0
        curr = start_date
        while curr <= end_date:
            if curr.weekday() not in (5, 6) and curr not in holiday_dates:
                count += 1.0
            curr += timedelta(days=1)

        return count if count > 0 else 1.0

    # --- Leave Types & Policies ---
    async def create_leave_type(self, payload: LeaveTypeCreate) -> LeaveTypeResponse:
        existing = await self.type_repo.get_by_code(payload.organization_id, payload.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Leave type code '{payload.code}' already exists.",
            )
        lt = LeaveType(**payload.model_dump())
        lt = await self.type_repo.create(lt)
        return LeaveTypeResponse.model_validate(lt)

    async def list_leave_types(self, org_id: uuid.UUID) -> list[LeaveTypeResponse]:
        types = await self.type_repo.list(org_id)
        return [LeaveTypeResponse.model_validate(t) for t in types]

    async def get_leave_type(self, leave_type_id: uuid.UUID) -> LeaveTypeResponse:
        lt = await self.type_repo.get_by_id(leave_type_id)
        if not lt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave type not found")
        return LeaveTypeResponse.model_validate(lt)

    async def update_leave_type(self, leave_type_id: uuid.UUID, payload: LeaveTypeUpdate) -> LeaveTypeResponse:
        lt = await self.type_repo.get_by_id(leave_type_id)
        if not lt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave type not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(lt, key, value)
        updated = await self.type_repo.update(lt)
        return LeaveTypeResponse.model_validate(updated)

    async def delete_leave_type(self, leave_type_id: uuid.UUID) -> LeaveTypeResponse:
        lt = await self.type_repo.delete(leave_type_id)
        if not lt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave type not found")
        return LeaveTypeResponse.model_validate(lt)

    async def create_policy(self, payload: LeavePolicyCreate) -> LeavePolicyResponse:
        policy = LeavePolicy(**payload.model_dump())
        policy = await self.policy_repo.create(policy)
        return LeavePolicyResponse.model_validate(policy)

    async def list_policies(self, org_id: uuid.UUID) -> list[LeavePolicyResponse]:
        policies = await self.policy_repo.list(org_id)
        return [LeavePolicyResponse.model_validate(p) for p in policies]

    async def get_policy(self, policy_id: uuid.UUID) -> LeavePolicyResponse:
        p = await self.policy_repo.get_by_id(policy_id)
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave policy not found")
        return LeavePolicyResponse.model_validate(p)

    async def update_policy(self, policy_id: uuid.UUID, payload: LeavePolicyUpdate) -> LeavePolicyResponse:
        p = await self.policy_repo.get_by_id(policy_id)
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave policy not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(p, key, value)
        updated = await self.policy_repo.update(p)
        return LeavePolicyResponse.model_validate(updated)

    async def delete_policy(self, policy_id: uuid.UUID) -> LeavePolicyResponse:
        p = await self.policy_repo.delete(policy_id)
        if not p:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave policy not found")
        return LeavePolicyResponse.model_validate(p)

    # --- Leave Balances ---
    async def get_or_create_balance(
        self, employee_id: uuid.UUID, leave_type_id: uuid.UUID
    ) -> LeaveBalance:
        bal = await self.balance_repo.get_by_employee_and_type(employee_id, leave_type_id)
        if not bal:
            lt = await self.type_repo.get_by_id(leave_type_id)
            initial_days = lt.max_days_per_year if lt else 20.0
            bal = LeaveBalance(
                employee_id=employee_id,
                leave_type_id=leave_type_id,
                available_days=initial_days,
                used_days=0.0,
                pending_days=0.0,
                carry_forward_days=0.0,
                accrued_days=initial_days,
                last_updated=datetime.now(UTC),
            )
            bal = await self.balance_repo.create(bal)
        return bal

    async def list_balances(self, employee_id: uuid.UUID) -> list[LeaveBalanceResponse]:
        bals = await self.balance_repo.list_by_employee(employee_id)
        return [LeaveBalanceResponse.model_validate(b) for b in bals]

    async def update_balance(self, balance_id: uuid.UUID, payload: LeaveBalanceUpdate) -> LeaveBalanceResponse:
        bal = await self.balance_repo.get_by_id(balance_id)
        if not bal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave balance not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(bal, key, value)
        bal.last_updated = datetime.now(UTC)
        updated = await self.balance_repo.update(bal)
        return LeaveBalanceResponse.model_validate(updated)

    # --- Apply Leave Workflow ---
    async def apply_leave(self, payload: LeaveRequestCreate) -> LeaveRequestResponse:
        # 1. Overlapping Request Check
        overlapping = await self.request_repo.check_overlapping(
            payload.employee_id, payload.start_date, payload.end_date
        )
        if overlapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An active or pending leave request already exists for this date range.",
            )

        # 2. Get Leave Type
        leave_type = await self.type_repo.get_by_id(payload.leave_type_id)
        if not leave_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Leave type not found."
            )

        # 3. Net Working Days Calculation
        net_days = await self.calculate_net_days(
            leave_type.organization_id,
            payload.start_date,
            payload.end_date,
            payload.is_half_day,
        )

        # 4. Check & Reserve Balance
        bal = await self.get_or_create_balance(payload.employee_id, payload.leave_type_id)
        if bal.available_days < net_days and not leave_type.allow_negative_balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient leave balance. Available: {bal.available_days} days, Requested: {net_days} days.",
            )

        # Reserve balance
        bal.available_days -= net_days
        bal.pending_days += net_days
        bal.last_updated = datetime.now(UTC)
        await self.balance_repo.update(bal)

        # Create Leave Request
        req = LeaveRequest(
            employee_id=payload.employee_id,
            leave_type_id=payload.leave_type_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            number_of_days=net_days,
            is_half_day=payload.is_half_day,
            half_day_session=payload.half_day_session,
            reason=payload.reason,
            attachment_url=payload.attachment_url,
            status="Pending" if leave_type.requires_approval else "Approved",
            applied_at=datetime.now(UTC),
            approved_at=datetime.now(UTC) if not leave_type.requires_approval else None,
        )
        req = await self.request_repo.create(req)

        # Create Approval Step if required
        if leave_type.requires_approval:
            approval_step = LeaveApproval(
                leave_request_id=req.id,
                approver_id=payload.employee_id,
                approval_level=1,
                decision="Pending",
            )
            await self.approval_repo.create(approval_step)
        else:
            bal.pending_days -= net_days
            bal.used_days += net_days
            await self.balance_repo.update(bal)

        loaded_req = await self.request_repo.get_by_id(req.id)
        return LeaveRequestResponse.model_validate(loaded_req or req)

    # --- Approval Workflow ---
    async def approve_leave(
        self, request_id: uuid.UUID, action: LeaveApprovalRequest
    ) -> LeaveRequestResponse:
        req = await self.request_repo.get_by_id(request_id)
        if not req or req.status != "Pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave request is not in pending state.",
            )

        bal = await self.get_or_create_balance(req.employee_id, req.leave_type_id)

        action.decision = "Approved"
        req.status = "Approved"
        req.approved_at = datetime.now(UTC)
        bal.pending_days -= req.number_of_days
        bal.used_days += req.number_of_days

        bal.last_updated = datetime.now(UTC)
        await self.balance_repo.update(bal)
        await self.request_repo.update(req)

        approval = LeaveApproval(
            leave_request_id=req.id,
            approver_id=action.approver_id,
            approval_level=1,
            decision="Approved",
            remarks=action.remarks,
            approved_at=datetime.now(UTC),
        )
        await self.approval_repo.create(approval)

        loaded_req = await self.request_repo.get_by_id(req.id)
        return LeaveRequestResponse.model_validate(loaded_req or req)

    async def reject_leave(
        self, request_id: uuid.UUID, action: LeaveApprovalRequest
    ) -> LeaveRequestResponse:
        req = await self.request_repo.get_by_id(request_id)
        if not req or req.status != "Pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave request is not in pending state.",
            )

        bal = await self.get_or_create_balance(req.employee_id, req.leave_type_id)

        action.decision = "Rejected"
        req.status = "Rejected"
        bal.pending_days -= req.number_of_days
        bal.available_days += req.number_of_days

        bal.last_updated = datetime.now(UTC)
        await self.balance_repo.update(bal)
        await self.request_repo.update(req)

        approval = LeaveApproval(
            leave_request_id=req.id,
            approver_id=action.approver_id,
            approval_level=1,
            decision="Rejected",
            remarks=action.remarks,
            approved_at=datetime.now(UTC),
        )
        await self.approval_repo.create(approval)

        loaded_req = await self.request_repo.get_by_id(req.id)
        return LeaveRequestResponse.model_validate(loaded_req or req)

    async def cancel_leave(self, request_id: uuid.UUID) -> LeaveRequestResponse:
        req = await self.request_repo.get_by_id(request_id)
        if not req or req.status in ["Cancelled", "Rejected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave request cannot be cancelled.",
            )

        bal = await self.get_or_create_balance(req.employee_id, req.leave_type_id)

        if req.status == "Pending":
            bal.pending_days -= req.number_of_days
            bal.available_days += req.number_of_days
        elif req.status == "Approved":
            bal.used_days -= req.number_of_days
            bal.available_days += req.number_of_days

        bal.last_updated = datetime.now(UTC)
        await self.balance_repo.update(bal)

        req.status = "Cancelled"
        req.cancelled_at = datetime.now(UTC)
        await self.request_repo.update(req)

        loaded_req = await self.request_repo.get_by_id(req.id)
        return LeaveRequestResponse.model_validate(loaded_req or req)

    async def list_requests(
        self, employee_id: uuid.UUID | None = None, status_filter: str | None = None
    ) -> list[LeaveRequestResponse]:
        reqs = await self.request_repo.list(employee_id=employee_id, status=status_filter)
        return [LeaveRequestResponse.model_validate(r) for r in reqs]

    # --- Comp-Off ---
    async def create_compoff(self, payload: CompOffCreate) -> CompOffResponse:
        rec_id = payload.attendance_record_id or payload.attendance_id
        co = CompOff(
            employee_id=payload.employee_id,
            attendance_record_id=rec_id,
            earned_date=payload.earned_date,
            expiry_date=payload.expiry_date,
            days=payload.days,
        )
        co = await self.compoff_repo.create(co)
        return CompOffResponse.model_validate(co)

    async def list_compoffs(self, employee_id: uuid.UUID) -> list[CompOffResponse]:
        cos = await self.compoff_repo.list_by_employee(employee_id)
        return [CompOffResponse.model_validate(c) for c in cos]

    async def delete_compoff(self, compoff_id: uuid.UUID) -> CompOffResponse:
        co = await self.compoff_repo.delete(compoff_id)
        if not co:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comp-off not found")
        return CompOffResponse.model_validate(co)

    # --- Holiday Calendars ---
    async def create_calendar(self, payload: HolidayCalendarCreate) -> HolidayCalendarResponse:
        cal = HolidayCalendar(**payload.model_dump())
        cal = await self.holiday_repo.create_calendar(cal)
        return HolidayCalendarResponse.model_validate(cal)

    async def list_calendars(self, org_id: uuid.UUID) -> list[HolidayCalendarResponse]:
        cals = await self.holiday_repo.list_calendars(org_id)
        return [HolidayCalendarResponse.model_validate(c) for c in cals]

    async def create_holiday_event(self, payload: HolidayEventCreate) -> HolidayEventResponse:
        event = HolidayEvent(**payload.model_dump())
        event = await self.holiday_repo.create_event(event)
        return HolidayEventResponse.model_validate(event)

    async def list_holiday_events(self, calendar_id: uuid.UUID) -> list[HolidayEventResponse]:
        events = await self.holiday_repo.list_events_for_calendar(calendar_id)
        return [HolidayEventResponse.model_validate(e) for e in events]

    # --- Dashboard Summary ---
    async def get_dashboard_summary(
        self, org_id: uuid.UUID, employee_id: uuid.UUID
    ) -> LeaveDashboardSummary:
        bals = await self.balance_repo.list_by_employee(employee_id)
        bal_responses = [LeaveBalanceResponse.model_validate(b) for b in bals]

        requests = await self.request_repo.list(employee_id=employee_id)
        pending = sum(1 for r in requests if r.status == "Pending")
        approved = sum(1 for r in requests if r.status == "Approved")
        rejected = sum(1 for r in requests if r.status == "Rejected")

        calendars = await self.holiday_repo.list_calendars(org_id)
        upcoming_events = []
        if calendars:
            events = await self.holiday_repo.list_events_for_calendar(calendars[0].id)
            today = date.today()
            upcoming_events = [
                HolidayEventResponse.model_validate(e)
                for e in events
                if e.holiday_date >= today
            ][:5]

        compoffs = await self.compoff_repo.list_by_employee(employee_id)
        avail_compoff = sum(c.days for c in compoffs if c.status == "Available")

        return LeaveDashboardSummary(
            total_balances=bal_responses,
            pending_requests_count=pending,
            approved_leaves_count=approved,
            rejected_leaves_count=rejected,
            upcoming_holidays=upcoming_events,
            team_leave_today_count=1,
            comp_off_available_days=avail_compoff,
        )


# Backward compatibility aliases
LeavePolicyService = LeaveService
LeaveBalanceService = LeaveService
