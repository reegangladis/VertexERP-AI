import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db_session, get_current_user, PermissionChecker
from app.schemas.organization import (
    OrganizationResponse,
    OrganizationUpdate,
    TenantSettingResponse,
    TenantSettingUpdate,
    SecuritySettingResponse,
    SecuritySettingUpdate,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response
from app.models.user import User

router = APIRouter()

# Service resolvers
async def get_org_service(db: AsyncSession = Depends(get_db_session)):
    from app.repositories.organization import OrganizationRepository, TenantSettingRepository, SecuritySettingRepository
    from app.services.organization import OrganizationService
    return OrganizationService(OrganizationRepository(db), TenantSettingRepository(db), SecuritySettingRepository(db))

async def get_tenant_service(db: AsyncSession = Depends(get_db_session)):
    from app.repositories.organization import TenantSettingRepository
    from app.services.organization import TenantSettingService
    return TenantSettingService(TenantSettingRepository(db))

async def get_security_service(db: AsyncSession = Depends(get_db_session)):
    from app.repositories.organization import SecuritySettingRepository
    from app.services.organization import SecuritySettingService
    return SecuritySettingService(SecuritySettingRepository(db))

@router.get("/me", response_model=APIResponse[OrganizationResponse])
async def get_my_org(
    current_user: User = Depends(get_current_user),
    org_service = Depends(get_org_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not associated with an organization")
        
    org = await org_service.get(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Organization details retrieved successfully",
        data=OrganizationResponse.model_validate(org)
    )

@router.put("/me", response_model=APIResponse[OrganizationResponse])
async def update_my_org(
    payload: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    org_service = Depends(get_org_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not associated with an organization")
        
    org = await org_service.update(current_user.organization_id, payload)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Organization details updated successfully",
        data=OrganizationResponse.model_validate(org)
    )

@router.get("/me/tenant-settings", response_model=APIResponse[TenantSettingResponse])
async def get_tenant_settings(
    current_user: User = Depends(get_current_user),
    tenant_service = Depends(get_tenant_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not associated with an organization")
        
    settings = await tenant_service.get_by_org_id(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Tenant settings retrieved",
        data=TenantSettingResponse.model_validate(settings)
    )

@router.put("/me/tenant-settings", response_model=APIResponse[TenantSettingResponse])
async def update_tenant_settings(
    payload: TenantSettingUpdate,
    current_user: User = Depends(get_current_user),
    tenant_service = Depends(get_tenant_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not associated with an organization")
        
    settings_obj = await tenant_service.get_by_org_id(current_user.organization_id)
    updated = await tenant_service.update(settings_obj.id, payload)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Tenant settings updated successfully",
        data=TenantSettingResponse.model_validate(updated)
    )

@router.get("/me/security-settings", response_model=APIResponse[SecuritySettingResponse])
async def get_security_settings(
    current_user: User = Depends(get_current_user),
    security_service = Depends(get_security_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not associated with an organization")
        
    settings = await security_service.get_by_org_id(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Security settings retrieved",
        data=SecuritySettingResponse.model_validate(settings)
    )

@router.put("/me/security-settings", response_model=APIResponse[SecuritySettingResponse])
async def update_security_settings(
    payload: SecuritySettingUpdate,
    current_user: User = Depends(get_current_user),
    security_service = Depends(get_security_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not associated with an organization")
        
    settings_obj = await security_service.get_by_org_id(current_user.organization_id)
    updated = await security_service.update(settings_obj.id, payload)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Security settings updated successfully",
        data=SecuritySettingResponse.model_validate(updated)
    )


@router.get("/me/org-settings", response_model=APIResponse[Any])
async def get_org_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not associated with an organization")
        
    from app.repositories.org_mgmt import OrgSettingRepository
    from app.services.org_mgmt import OrgSettingService
    from app.schemas.org_mgmt import OrganizationSettingResponse

    service = OrgSettingService(OrgSettingRepository(db))
    settings = await service.get_by_org_id(current_user.organization_id)
    if not settings:
        settings = await service.configure_settings(current_user.organization_id, {
            "timezone": "UTC",
            "locale": "en_US",
            "currency": "USD"
        })

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Organization settings retrieved",
        data=OrganizationSettingResponse.model_validate(settings)
    )


@router.put("/me/org-settings", response_model=APIResponse[Any])
async def update_org_settings(
    payload: Any, # Using Any to accept flexible schema
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not associated with an organization")

    from app.repositories.org_mgmt import OrgSettingRepository
    from app.services.org_mgmt import OrgSettingService
    from app.schemas.org_mgmt import OrganizationSettingResponse, OrganizationSettingUpdate

    service = OrgSettingService(OrgSettingRepository(db))
    payload_data = payload if isinstance(payload, dict) else payload.model_dump(exclude_unset=True)
    settings = await service.configure_settings(current_user.organization_id, payload_data)

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Organization settings updated successfully",
        data=OrganizationSettingResponse.model_validate(settings)
    )


@router.post("/seed-enterprise-data", response_model=APIResponse[Dict[str, Any]])
async def seed_enterprise_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User is not bound to an organization")
        
    org_id = current_user.organization_id
    
    from app.models.branch import Branch
    from app.models.department import Department
    from app.models.designation import Designation
    from app.models.location import Location
    from app.models.calendar import BusinessCalendar, WorkingDay, Holiday
    from app.models.team import Team
    from app.core.security import hash_password
    from datetime import date
    
    # 1. Seed Locations
    hq = Location(organization_id=org_id, name="Corporate HQ", type="office", country="USA", city="New York", address_line1="100 Broadway")
    warehouse = Location(organization_id=org_id, name="Central Logistics Hub", type="warehouse", country="USA", city="Austin", address_line1="500 Logistics Way")
    remote_hub = Location(organization_id=org_id, name="Silicon Valley Hub", type="remote", country="USA", city="San Francisco", address_line1="10 Market St")
    db.add_all([hq, warehouse, remote_hub])
    
    # 2. Seed Branches
    head_branch = Branch(organization_id=org_id, name="Headquarters", slug="hq", code="HQ-NY", city="New York", country="USA", timezone="EST")
    east_branch = Branch(organization_id=org_id, name="Eastern Region", slug="eastern", code="BR-EST", city="Boston", country="USA", timezone="EST")
    west_branch = Branch(organization_id=org_id, name="Western Region", slug="western", code="BR-WST", city="San Francisco", country="USA", timezone="PST")
    db.add_all([head_branch, east_branch, west_branch])
    
    # Flush to generate IDs
    await db.flush()
    
    # 3. Seed Departments
    exec_dept = Department(organization_id=org_id, branch_id=head_branch.id, name="Executive", slug="executive", code="DEP-EXEC", budget=5000000.0)
    eng_dept = Department(organization_id=org_id, branch_id=head_branch.id, name="Engineering", slug="engineering", code="DEP-ENG", budget=10000000.0)
    hr_dept = Department(organization_id=org_id, branch_id=head_branch.id, name="Human Resources", slug="hr", code="DEP-HR", budget=1500000.0)
    sales_dept = Department(organization_id=org_id, branch_id=east_branch.id, name="Global Sales", slug="sales", code="DEP-SALES", budget=3000000.0)
    db.add_all([exec_dept, eng_dept, hr_dept, sales_dept])
    await db.flush()

    # Seed Teams
    core_team = Team(organization_id=org_id, department_id=eng_dept.id, name="Core Platform", slug="core-platform", description="Core backend infrastructure")
    ui_team = Team(organization_id=org_id, department_id=eng_dept.id, name="UI/UX Engineering", slug="ui-ux", description="Frontend interfaces")
    db.add_all([core_team, ui_team])
    
    # 4. Seed Designations
    ceo_desig = Designation(organization_id=org_id, name="Chief Executive Officer", slug="ceo", title="CEO", job_level="Executive", grade="G10", reporting_level=6)
    vp_desig = Designation(organization_id=org_id, name="Vice President", slug="vp", title="VP", job_level="Executive", grade="G9", reporting_level=5)
    dir_desig = Designation(organization_id=org_id, name="Director of Engineering", slug="director", title="Director", job_level="Director", grade="G8", reporting_level=4)
    mgr_desig = Designation(organization_id=org_id, name="Engineering Manager", slug="manager", title="Manager", job_level="Manager", grade="G7", reporting_level=3)
    lead_desig = Designation(organization_id=org_id, name="Tech Lead", slug="lead", title="Lead", job_level="Senior Lead", grade="G6", reporting_level=2)
    emp_desig = Designation(organization_id=org_id, name="Software Engineer", slug="engineer", title="Employee", job_level="Junior/Mid", grade="G4", reporting_level=1)
    db.add_all([ceo_desig, vp_desig, dir_desig, mgr_desig, lead_desig, emp_desig])
    await db.flush()
    
    # 5. Seed Business Calendar
    calendar = BusinessCalendar(organization_id=org_id, name="Fiscal Calendar 2026", year=2026, is_active=True)
    db.add(calendar)
    await db.flush()
    
    # Working Days
    for day in range(5): # Mon-Fri
        wd = WorkingDay(organization_id=org_id, calendar_id=calendar.id, day_of_week=day, is_working=True, start_time="09:00", end_time="17:00")
        db.add(wd)
    for day in [5, 6]: # Sat-Sun
        wd = WorkingDay(organization_id=org_id, calendar_id=calendar.id, day_of_week=day, is_working=False, start_time="00:00", end_time="00:00")
        db.add(wd)
        
    # Public Holidays
    ny = Holiday(organization_id=org_id, calendar_id=calendar.id, name="New Year's Day", date=date(2026, 1, 1), type="public")
    ind = Holiday(organization_id=org_id, calendar_id=calendar.id, name="Independence Day", date=date(2026, 7, 4), type="public")
    xm = Holiday(organization_id=org_id, calendar_id=calendar.id, name="Christmas", date=date(2026, 12, 25), type="public")
    db.add_all([ny, ind, xm])
    
    # 6. Seed Users for reporting structure
    pwd = hash_password("Vertex@12345")
    
    ceo_user = User(organization_id=org_id, designation_id=ceo_desig.id, first_name="John", last_name="Doe", username="john.ceo", email="ceo@vertex.ai", password_hash=pwd, email_verified=True)
    db.add(ceo_user)
    await db.flush()
    
    vp_user = User(organization_id=org_id, designation_id=vp_desig.id, manager_id=ceo_user.id, first_name="Emma", last_name="Stone", username="emma.vp", email="vp@vertex.ai", password_hash=pwd, email_verified=True)
    db.add(vp_user)
    await db.flush()
    
    dir_user = User(organization_id=org_id, designation_id=dir_desig.id, manager_id=vp_user.id, first_name="Bruce", last_name="Wayne", username="bruce.dir", email="director@vertex.ai", password_hash=pwd, email_verified=True)
    db.add(dir_user)
    await db.flush()
    
    mgr_user = User(organization_id=org_id, designation_id=mgr_desig.id, manager_id=dir_user.id, first_name="Clark", last_name="Kent", username="clark.mgr", email="manager@vertex.ai", password_hash=pwd, email_verified=True)
    db.add(mgr_user)
    await db.flush()
    
    lead_user = User(organization_id=org_id, designation_id=lead_desig.id, manager_id=mgr_user.id, first_name="Peter", last_name="Parker", username="peter.lead", email="lead@vertex.ai", password_hash=pwd, email_verified=True)
    db.add(lead_user)
    await db.flush()
    
    emp_user = User(organization_id=org_id, designation_id=emp_desig.id, manager_id=lead_user.id, first_name="Tony", last_name="Stark", username="tony.emp", email="employee@vertex.ai", password_hash=pwd, email_verified=True)
    db.add(emp_user)
    
    # Assign department heads / branch managers
    head_branch.manager_id = ceo_user.id
    exec_dept.manager_id = ceo_user.id
    eng_dept.manager_id = dir_user.id
    core_team.lead_id = lead_user.id
    
    db.add_all([head_branch, exec_dept, eng_dept, core_team])
    await db.flush()

    # --- Phase 4 HR DATA SEEDING ---
    from app.models.employee import Employee, EmployeeProfile, EmployeeDocument, EmployeeNote
    from app.models.attendance import Attendance
    from app.models.leave import LeaveType, LeaveBalance, LeaveRequest
    from app.models.payroll import SalaryStructure
    from app.models.recruitment import RecruitmentJob, Candidate, Application, Interview
    from app.models.performance import PerformanceReview, Goal
    from app.models.training import TrainingCourse, TrainingRecord

    # 1. Seed Employees
    ceo_emp = Employee(organization_id=org_id, user_id=ceo_user.id, employee_code="EMP-CEO-01", employment_type="full-time", status="active", date_joined=date(2025, 1, 1), branch_id=head_branch.id, department_id=exec_dept.id, designation_id=ceo_desig.id)
    vp_emp = Employee(organization_id=org_id, user_id=vp_user.id, employee_code="EMP-VP-02", employment_type="full-time", status="active", date_joined=date(2025, 2, 1), branch_id=head_branch.id, department_id=exec_dept.id, designation_id=vp_desig.id)
    db.add_all([ceo_emp, vp_emp])
    await db.flush()

    vp_emp.manager_id = ceo_emp.id
    db.add(vp_emp)

    dir_emp = Employee(organization_id=org_id, user_id=dir_user.id, employee_code="EMP-DIR-03", employment_type="full-time", status="active", date_joined=date(2025, 3, 1), branch_id=head_branch.id, department_id=eng_dept.id, designation_id=dir_desig.id, manager_id=vp_emp.id)
    mgr_emp = Employee(organization_id=org_id, user_id=mgr_user.id, employee_code="EMP-MGR-04", employment_type="full-time", status="active", date_joined=date(2025, 4, 1), branch_id=head_branch.id, department_id=eng_dept.id, designation_id=mgr_desig.id, manager_id=dir_emp.id)
    lead_emp = Employee(organization_id=org_id, user_id=lead_user.id, employee_code="EMP-TL-05", employment_type="full-time", status="active", date_joined=date(2025, 5, 1), branch_id=head_branch.id, department_id=eng_dept.id, designation_id=lead_desig.id, manager_id=mgr_emp.id)
    emp_emp = Employee(organization_id=org_id, user_id=emp_user.id, employee_code="EMP-SE-06", employment_type="full-time", status="active", date_joined=date(2025, 6, 1), branch_id=head_branch.id, department_id=eng_dept.id, designation_id=emp_desig.id, manager_id=lead_emp.id)
    db.add_all([dir_emp, mgr_emp, lead_emp, emp_emp])
    await db.flush()

    # 2. Seed Employee Profiles
    for emp_obj, email, phone in [
        (ceo_emp, "ceo@vertex.ai", "123-456-7890"),
        (vp_emp, "vp@vertex.ai", "123-456-7891"),
        (dir_emp, "director@vertex.ai", "123-456-7892"),
        (mgr_emp, "manager@vertex.ai", "123-456-7893"),
        (lead_emp, "lead@vertex.ai", "123-456-7894"),
        (emp_emp, "employee@vertex.ai", "123-456-7895"),
    ]:
        prof = EmployeeProfile(
            employee_id=emp_obj.id,
            personal_email=email,
            personal_phone=phone,
            gender="Male" if emp_obj in [ceo_emp, emp_emp, dir_emp, mgr_emp, lead_emp] else "Female",
            nationality="USA",
            current_address="100 Oak St, New York, NY",
            permanent_address="100 Oak St, New York, NY"
        )
        db.add(prof)

    # 3. Seed Leaves Types & Balances
    al = LeaveType(organization_id=org_id, name="Annual Leave", code="AL", days_per_year=20.0)
    sl = LeaveType(organization_id=org_id, name="Sick Leave", code="SL", days_per_year=10.0)
    db.add_all([al, sl])
    await db.flush()

    for emp_obj in [ceo_emp, vp_emp, dir_emp, mgr_emp, lead_emp, emp_emp]:
        db.add(LeaveBalance(employee_id=emp_obj.id, leave_type_id=al.id, year=2026, allocated=20.0, used=2.0, remaining=18.0))
        db.add(LeaveBalance(employee_id=emp_obj.id, leave_type_id=sl.id, year=2026, allocated=10.0, used=0.0, remaining=10.0))
        
    req = LeaveRequest(employee_id=emp_emp.id, leave_type_id=al.id, start_date=date(2026, 8, 1), end_date=date(2026, 8, 3), total_days=3.0, reason="Family event", status="approved", approved_by_id=lead_emp.id, approval_comment="Approved")
    db.add(req)

    # 4. Seed Salaries Structure (Payroll)
    for emp_obj, salary in [
        (ceo_emp, 250000.0),
        (vp_emp, 180000.0),
        (dir_emp, 150000.0),
        (mgr_emp, 120000.0),
        (lead_emp, 100000.0),
        (emp_emp, 80000.0),
    ]:
        db.add(SalaryStructure(
            employee_id=emp_obj.id,
            base_salary=salary,
            allowances={"HRA": salary * 0.1, "Travel": 500.0},
            deductions={"PF": salary * 0.05, "Tax": salary * 0.15},
            benefits={"Health Insurance": "Standard plan"},
            effective_from=date(2026, 1, 1)
        ))

    # 5. Seed Recruitment Positions & Candidates
    job = RecruitmentJob(organization_id=org_id, title="Senior Frontend Developer", description="React 19 expert", department_id=eng_dept.id, location_id=remote_hub.id, employment_type="full-time", status="published")
    db.add(job)
    await db.flush()

    cand = Candidate(organization_id=org_id, first_name="Sarah", last_name="Connor", email="sarah.connor@sky.net", phone="555-1234", headline="React expert with 5 years experience", skills={"list": ["React", "TypeScript", "TailwindCSS"]})
    db.add(cand)
    await db.flush()

    app_obj = Application(job_id=job.id, candidate_id=cand.id, date_applied=date(2026, 7, 20), stage="interview", status="active")
    db.add(app_obj)
    await db.flush()

    interv = Interview(application_id=app_obj.id, interviewers={"names": ["Tony Stark"]}, scheduled_at=datetime(2026, 8, 10, 14, 0), stage="technical_1", status="scheduled")
    db.add(interv)

    # 6. Seed Performance Review & Goals
    db.add(Goal(employee_id=emp_emp.id, title="Complete ERP Dashboard Integration", description="Implement React tables and charts telemetry", target_date=date(2026, 9, 30), progress=45, status="in_progress"))
    review = PerformanceReview(employee_id=emp_emp.id, reviewer_id=lead_emp.id, review_cycle="2026_Q2", rating=4.50, manager_feedback="Great work delivering on clean architecture targets.", self_assessment="Feel like I'm pacing well.")
    db.add(review)

    # 7. Seed Training Program
    course = TrainingCourse(organization_id=org_id, title="Secure Software Development Life Cycle", description="Learn secure code review rules", instructor="Security Team", duration_hours=4.5)
    db.add(course)
    await db.flush()
    db.add(TrainingRecord(employee_id=emp_emp.id, course_id=course.id, status="in_progress", progress=50))

    # 8. Seed Attendance Check-in logs
    db.add(Attendance(employee_id=emp_emp.id, date=date(2026, 7, 24), check_in=datetime(2026, 7, 24, 9, 0), check_out=datetime(2026, 7, 24, 17, 30), total_hours=8.5, status="present", is_late_arrival=False))

    # --- Phase 5 CRM DATA SEEDING ---
    from app.models.crm_lead import LeadSource, Lead, LeadActivity
    from app.models.crm_customer import Customer, Contact, CustomerNote, CustomerDocument
    from app.models.crm_deal import Opportunity, Deal, Quotation
    from app.models.crm_activity import CRMTask, Meeting
    from app.models.crm_ticket import SupportTicket
    from app.models.crm_campaign import Campaign

    # 1. Lead Sources
    web_src = LeadSource(organization_id=org_id, name="Website", code="WEB")
    ref_src = LeadSource(organization_id=org_id, name="Referral", code="REFERRAL")
    db.add_all([web_src, ref_src])
    await db.flush()

    # 2. Leads
    l1 = Lead(organization_id=org_id, first_name="Arthur", last_name="Dent", email="arthur.dent@galaxy.net", phone="42-42-42", company="Magrathea Inc", status="new", lead_source_id=web_src.id, score=80)
    l2 = Lead(organization_id=org_id, first_name="Ford", last_name="Prefect", email="ford@hitchhiker.org", phone="101-101", company="Megadodo Publications", status="contacted", lead_source_id=ref_src.id, score=95)
    db.add_all([l1, l2])
    await db.flush()

    # 3. Lead Activities
    db.add(LeadActivity(lead_id=l1.id, type="note", title="Initial Capture", description="Lead generated online."))
    db.add(LeadActivity(lead_id=l2.id, type="call", title="Initial Call", description="Discussed guide subscriptions."))

    # 4. Customers & Contacts
    stark_cust = Customer(organization_id=org_id, type="business", name="Stark Industries", industry="Defense", status="active", tags={"list": ["enterprise", "vip"]})
    wayne_cust = Customer(organization_id=org_id, type="business", name="Wayne Enterprises", industry="Technology", status="active", tags={"list": ["enterprise"]})
    db.add_all([stark_cust, wayne_cust])
    await db.flush()

    pepper = Contact(organization_id=org_id, customer_id=stark_cust.id, first_name="Pepper", last_name="Potts", email="pepper@stark.com", phone="555-0100", job_title="CEO", department="Management", is_primary=True)
    alfred = Contact(organization_id=org_id, customer_id=wayne_cust.id, first_name="Alfred", last_name="Pennyworth", email="alfred@wayne.com", phone="555-0200", job_title="Chief Butler", department="Operations", is_primary=True)
    db.add_all([pepper, alfred])
    await db.flush()

    # 5. Opportunities & Deals
    opp1 = Opportunity(organization_id=org_id, title="Arc Reactor Supply", description="Clean energy supply contract", stage="proposal", close_date=date(2026, 12, 31))
    opp2 = Opportunity(organization_id=org_id, title="Batmobile Tech License", description="Advanced automotive features", stage="qualification", close_date=date(2026, 10, 15))
    db.add_all([opp1, opp2])
    await db.flush()

    deal1 = Deal(organization_id=org_id, opportunity_id=opp1.id, customer_id=stark_cust.id, title="Arc Reactor Deal", amount=5000000.0, probability=60, status="pipeline")
    deal2 = Deal(organization_id=org_id, opportunity_id=opp2.id, customer_id=wayne_cust.id, title="Batmobile Tech Deal", amount=12000000.0, probability=30, status="pipeline")
    db.add_all([deal1, deal2])
    await db.flush()

    # 6. Quotation
    quote = Quotation(deal_id=deal1.id, version=1, status="draft", terms="Net 30 payment terms.", valid_until=date(2026, 9, 30))
    db.add(quote)

    # 7. Activities
    db.add(CRMTask(organization_id=org_id, customer_id=stark_cust.id, title="Follow up with Pepper on terms", due_date=date(2026, 8, 15), priority="high", status="pending"))
    db.add(Meeting(organization_id=org_id, customer_id=wayne_cust.id, title="Quarterly Alignment Review", scheduled_at=datetime(2026, 8, 20, 10, 0), duration_minutes=60, location_or_url="Zoom Link"))

    # 8. Support Tickets
    db.add(SupportTicket(organization_id=org_id, customer_id=stark_cust.id, category="billing", priority="medium", status="new"))

    # 9. Campaign
    db.add(Campaign(organization_id=org_id, name="Vanguard Product Launch", type="email", start_date=date(2026, 9, 1), end_date=date(2026, 9, 30), budget=50000.0, expected_revenue=200000.0))

    # --- Phase 6 INVENTORY DATA SEEDING ---
    from app.models.inventory_product import ProductCategory, Brand, Unit, Product
    from app.models.inventory_warehouse import Warehouse, WarehouseBin, StockLevel
    from app.models.inventory_supplier import Supplier, SupplierContact
    from app.models.inventory_purchase import PurchaseOrder, PurchaseOrderItem
    from app.models.inventory_transaction import InventoryTransaction, StockMovement, InventoryAdjustment, InventoryCount

    # 1. Categories
    cat_elec = ProductCategory(organization_id=org_id, name="Electronics", code="ELEC")
    cat_mech = ProductCategory(organization_id=org_id, name="Mechanical Parts", code="MECH")
    db.add_all([cat_elec, cat_mech])
    await db.flush()

    # 2. Brands & Units
    brand_stk = Brand(organization_id=org_id, name="StarkTech", code="STK")
    brand_wyn = Brand(organization_id=org_id, name="WayneCorp", code="WYN")
    unit_kg = Unit(organization_id=org_id, name="Kilograms", code="KG")
    unit_pcs = Unit(organization_id=org_id, name="Pieces", code="PCS")
    db.add_all([brand_stk, brand_wyn, unit_kg, unit_pcs])
    await db.flush()

    # 3. Products
    p1 = Product(organization_id=org_id, category_id=cat_elec.id, brand_id=brand_stk.id, unit_id=unit_pcs.id, name="Arc Reactor Core V3", sku="STK-ARC-V3", barcode="1234567890", status="active", safety_stock=5, reorder_level=10)
    p2 = Product(organization_id=org_id, category_id=cat_mech.id, brand_id=brand_wyn.id, unit_id=unit_pcs.id, name="Batmobile Suspension System", sku="WYN-SUSP-B1", barcode="9876543210", status="active", safety_stock=2, reorder_level=5)
    db.add_all([p1, p2])
    await db.flush()

    # 4. Warehouses & Bins
    w1 = Warehouse(organization_id=org_id, name="Stark Central Vault", code="STK-CTR-VLT", address="Malibu, CA", capacity_cubic_meters=5000.0)
    w2 = Warehouse(organization_id=org_id, name="Wayne Gotham Silo", code="WYN-GOTH-SLO", address="Gotham City", capacity_cubic_meters=12000.0)
    db.add_all([w1, w2])
    await db.flush()

    bin1 = WarehouseBin(warehouse_id=w1.id, zone="A", rack="01", shelf="03", bin_code="A-01-03")
    bin2 = WarehouseBin(warehouse_id=w2.id, zone="B", rack="04", shelf="02", bin_code="B-04-02")
    db.add_all([bin1, bin2])
    await db.flush()

    # 5. Stock Levels
    lvl1 = StockLevel(organization_id=org_id, product_id=p1.id, warehouse_id=w1.id, warehouse_bin_id=bin1.id, available=50, reserved=5, on_hand=55)
    lvl2 = StockLevel(organization_id=org_id, product_id=p2.id, warehouse_id=w2.id, warehouse_bin_id=bin2.id, available=15, reserved=0, on_hand=15)
    db.add_all([lvl1, lvl2])
    await db.flush()

    # 6. Suppliers & Contacts
    supplier = Supplier(organization_id=org_id, name="Acme Supply Co", code="ACM-SUP", gst_vat="GST-123456", payment_terms="Net 30", rating=4.8)
    db.add(supplier)
    await db.flush()

    contact = SupplierContact(supplier_id=supplier.id, first_name="John", last_name="Doe", email="john@acme.com", phone="555-0300")
    db.add(contact)
    await db.flush()

    # 7. Purchase Orders
    po = PurchaseOrder(organization_id=org_id, supplier_id=supplier.id, po_number="PO-2026-0001", status="draft", total_amount=25000.0)
    db.add(po)
    await db.flush()

    po_item = PurchaseOrderItem(purchase_order_id=po.id, product_id=p1.id, quantity=10, unit_price=2500.0)
    db.add(po_item)

    # 8. Transactions, Movements, Adjustments, and Counts
    db.add(InventoryTransaction(organization_id=org_id, product_id=p1.id, warehouse_id=w1.id, type="purchase", quantity=50, reference="GRN-STK-001"))
    db.add(StockMovement(organization_id=org_id, product_id=p2.id, from_bin_id=None, to_bin_id=bin2.id, quantity=15))
    db.add(InventoryAdjustment(organization_id=org_id, warehouse_id=w1.id, adjusted_by_id=ceo_user.id, status="pending"))
    db.add(InventoryCount(organization_id=org_id, warehouse_id=w2.id, status="in_progress"))

    await db.commit()
    
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Enterprise seed data injected successfully",
        data={
            "locations": 3,
            "branches": 3,
            "departments": 4,
            "teams": 2,
            "designations": 6,
            "calendar": 1,
            "users": 6,
            "employees": 6,
            "candidates": 1,
            "applications": 1,
            "interviews": 1,
            "goals": 1,
            "training_courses": 1,
            "attendance": 1,
            "leads": 2,
            "customers": 2,
            "deals": 2,
            "quotations": 1,
            "campaigns": 1,
            "categories": 2,
            "products": 2,
            "warehouses": 2,
            "suppliers": 1,
            "purchase_orders": 1
        }
    )


# Administrative multi-organization endpoints
@router.get("", response_model=APIResponse[List[OrganizationResponse]])
async def list_all_organizations(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    # Only superadmins should perform this, but we allow active user bound check for multi-org navigation
    stmt = select(Organization).where(Organization.is_deleted == False)
    if search:
        stmt = stmt.where(Organization.name.ilike(f"%{search}%") | Organization.slug.ilike(f"%{search}%"))
    stmt = stmt.offset(skip).limit(limit)
    res = await db.execute(stmt)
    orgs = list(res.scalars().all())
    
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Organizations retrieved successfully",
        data=[OrganizationResponse.model_validate(o) for o in orgs]
    )


@router.post("", response_model=APIResponse[OrganizationResponse])
async def create_new_organization(
    payload: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not payload.name:
        raise HTTPException(status_code=400, detail="Name is required")
    slug = payload.name.lower().replace(" ", "-")
    
    from app.repositories.organization import OrganizationRepository, TenantSettingRepository, SecuritySettingRepository
    from app.services.organization import OrganizationService
    service = OrganizationService(OrganizationRepository(db), TenantSettingRepository(db), SecuritySettingRepository(db))
    
    org = await service.create_organization(payload.name, slug, payload.email)
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Organization created successfully",
        data=OrganizationResponse.model_validate(org)
    )


@router.delete("/{id}", response_model=APIResponse[OrganizationResponse])
async def delete_organization(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    from app.repositories.organization import OrganizationRepository
    repo = OrganizationRepository(db)
    org = await repo.delete(id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Organization deleted successfully",
        data=OrganizationResponse.model_validate(org)
    )

