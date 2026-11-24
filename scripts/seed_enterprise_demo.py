"""Enterprise Demo Data Seeder for VertexERP AI.

Provisions an enterprise tenant ("Apex Global Holdings"), dual-workspace users,
departments, designations, shifts, employees, 30-day attendance history,
leave balances, CRM leads, accounts, contacts, pipeline deals, quotations,
and confirmed sales orders.

Usage:
    python scripts/seed_enterprise_demo.py
"""

import asyncio
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
import uuid

from sqlalchemy import select

from app.core.logging import logger, setup_logging
from app.core.security import hash_password
from app.infrastructure.database.session import async_session_factory, close_db_engine
from app.modules.crm.models import (
    Activity,
    Contact,
    Customer,
    Deal,
    Lead,
    Quotation,
    QuotationItem,
    SalesOrder,
    SalesOrderItem,
)
from app.modules.hr.models.attendance import AttendanceRecord, Shift
from app.modules.hr.models.employee import Employee
from app.modules.hr.models.leave import LeaveBalance, LeaveType
from app.modules.identity.models.role import Role, UserRole
from app.modules.identity.models.user import User
from app.modules.identity.models.user_credential import UserCredential
from app.modules.organization.models.department import Department
from app.modules.organization.models.designation import Designation
from app.modules.organization.models.organization import Organization
from app.modules.organization.models.tenant import Tenant


async def seed_enterprise_demo() -> None:
    setup_logging()
    logger.info("Initializing Enterprise Demo Seeder for VertexERP AI...")
    from app.infrastructure.database.session import init_db_engine
    await init_db_engine()

    async with async_session_factory() as session:
        # 1. Provision Tenant
        res = await session.execute(select(Tenant).where(Tenant.slug == "apex"))
        tenant = res.scalar_one_or_none()

        if not tenant:
            tenant = Tenant(
                id=uuid.uuid4(),
                name="Apex Global Holdings",
                slug="apex",
                is_active=True,
            )
            session.add(tenant)
            await session.flush()
            logger.info("Provisioned Tenant: %s (%s)", tenant.name, tenant.slug)
        else:
            logger.info("Existing Tenant 'apex' found.")

        # 2. Provision Organization
        res_org = await session.execute(
            select(Organization).where(Organization.tenant_id == tenant.id)
        )
        org = res_org.scalars().first()

        if not org:
            org = Organization(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                name="Apex Commercial Enterprise",
                legal_name="Apex Global Enterprises International Inc.",
                tax_identifier="US-EIN-987654321",
                base_currency="USD",
                is_active=True,
            )
            session.add(org)
            await session.flush()
            logger.info("Provisioned Organization: %s", org.name)

        # 3. Create or Find Core Roles
        roles_spec = [
            ("SUPER_ADMIN", "Full platform administration across all tenants and workspaces"),
            ("ORG_ADMIN", "Organization-wide operational control and configuration"),
            ("HR_MANAGER", "Human resources, payroll, and attendance administration"),
            ("SALES_MANAGER", "CRM, deals, quotations, and revenue operations"),
            ("FINANCE_MANAGER", "General ledger, invoicing, and fiscal reporting"),
            ("EMPLOYEE", "Employee self-service and personal request portal access"),
        ]

        role_map: dict[str, Role] = {}
        for r_name, r_desc in roles_spec:
            r_res = await session.execute(
                select(Role).where(Role.tenant_id == tenant.id, Role.name == r_name)
            )
            r = r_res.scalar_one_or_none()
            if not r:
                r = Role(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    name=r_name,
                    code=r_name,
                    description=r_desc,
                    is_system_role=True,
                )
                session.add(r)
                await session.flush()
            role_map[r_name] = r

        # 4. Provision Users with Argon2 credentials
        users_spec = [
            ("admin@vertexerp.com", "System", "Administrator", "SUPER_ADMIN"),
            ("hr@vertexerp.com", "Eleanor", "Vance", "HR_MANAGER"),
            ("sales@vertexerp.com", "Marcus", "Sterling", "SALES_MANAGER"),
            ("finance@vertexerp.com", "Victoria", "Chase", "FINANCE_MANAGER"),
            ("employee@vertexerp.com", "Alex", "Morgan", "EMPLOYEE"),
            # Learnova & Reference Screenshot Demo Personas
            ("reegangladis@gmail.com", "Reegan", "Gladis", "SUPER_ADMIN"),
            ("admin@learnova.ai", "Platform", "Admin", "SUPER_ADMIN"),
            ("student@learnova.ai", "Enrolled", "Student", "EMPLOYEE"),
            ("instructor@learnova.ai", "Lead", "Instructor", "SALES_MANAGER"),
            ("superadmin@learnova.ai", "Chief", "Super Admin", "SUPER_ADMIN"),
        ]

        user_map: dict[str, User] = {}
        hashed_pw = hash_password("DemoPassword123!")

        for email, first, last, r_name in users_spec:
            u_res = await session.execute(
                select(User).where(User.tenant_id == tenant.id, User.email == email)
            )
            u = u_res.scalar_one_or_none()
            if not u:
                u = User(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    default_organization_id=org.id,
                    email=email,
                    full_name=f"{first} {last}",
                    is_active=True,
                    is_verified=True,
                )
                session.add(u)
                await session.flush()

                cred = UserCredential(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    user_id=u.id,
                    password_hash=hashed_pw,
                    salt="vertexerp_demo_salt",
                )
                session.add(cred)

                # Link user role
                target_role = role_map[r_name]
                ur = UserRole(
                    id=uuid.uuid4(),
                    user_id=u.id,
                    role_id=target_role.id,
                    tenant_id=tenant.id,
                    organization_id=org.id,
                )
                session.add(ur)
                await session.flush()
                logger.info("Created User [%s]: %s (%s)", r_name, email, u.id)
            user_map[email] = u

        # 5. Provision Departments & Designations
        dept_names = ["Engineering & Technology", "Sales & Commercial", "People Operations", "Finance & Corporate"]
        dept_map: dict[str, Department] = {}
        for d_name in dept_names:
            d_res = await session.execute(
                select(Department).where(Department.tenant_id == tenant.id, Department.name == d_name)
            )
            d = d_res.scalar_one_or_none()
            if not d:
                d = Department(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    organization_id=org.id,
                    name=d_name,
                    code=d_name[:4].upper(),
                    is_active=True,
                )
                session.add(d)
                await session.flush()
            dept_map[d_name] = d

        desig_names = [
            "Lead Systems Architect",
            "Senior Enterprise Account Executive",
            "HR Business Partner",
            "Financial Controller",
        ]
        desig_map: dict[str, Designation] = {}
        for d_title in desig_names:
            ds_res = await session.execute(
                select(Designation).where(Designation.tenant_id == tenant.id, Designation.name == d_title)
            )
            ds = ds_res.scalar_one_or_none()
            if not ds:
                ds = Designation(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    organization_id=org.id,
                    name=d_title,
                    code=d_title[:4].upper(),
                    is_active=True,
                )
                session.add(ds)
                await session.flush()
            desig_map[d_title] = ds

        # 6. Work Shift
        shift_res = await session.execute(
            select(Shift).where(Shift.tenant_id == tenant.id, Shift.code == "GEN-01")
        )
        shift = shift_res.scalar_one_or_none()
        if not shift:
            shift = Shift(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                organization_id=org.id,
                code="GEN-01",
                name="Standard General Shift (09:00 - 18:00)",
                start_time="09:00:00",
                end_time="18:00:00",
                grace_period_minutes=15,
                break_duration_minutes=60,
            )
            session.add(shift)
            await session.flush()

        # 7. Provision Employees
        emp_specs = [
            ("employee@vertexerp.com", "Alex", "Morgan", "EMP-001", "Engineering & Technology", "Lead Systems Architect"),
            ("sales@vertexerp.com", "Marcus", "Sterling", "EMP-002", "Sales & Commercial", "Senior Enterprise Account Executive"),
            ("hr@vertexerp.com", "Eleanor", "Vance", "EMP-003", "People Operations", "HR Business Partner"),
        ]

        emp_map: dict[str, Employee] = {}
        for email, first, last, emp_code, d_name, des_name in emp_specs:
            target_user = user_map[email]
            e_res = await session.execute(
                select(Employee).where(Employee.tenant_id == tenant.id, Employee.employee_number == emp_code)
            )
            e = e_res.scalar_one_or_none()
            if not e:
                e = Employee(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    organization_id=org.id,
                    user_id=target_user.id,
                    employee_number=emp_code,
                    first_name=first,
                    last_name=last,
                    email=email,
                    department_id=dept_map[d_name].id,
                    designation_id=desig_map[des_name].id,
                    hire_date=date(2024, 1, 15),
                    employment_status="ACTIVE",
                )
                session.add(e)
                await session.flush()
                logger.info("Provisioned Employee Record: %s (%s)", emp_code, email)
            emp_map[email] = e

        alex_emp = emp_map["employee@vertexerp.com"]

        # 8. Leave Types & Quotas
        leave_types = [
            ("PAID", "Annual Paid Leave", 18.0),
            ("SICK", "Sick & Medical Leave", 12.0),
            ("CASUAL", "Casual Discretionary Leave", 6.0),
        ]
        curr_year = datetime.now(UTC).year

        for lt_code, lt_name, total_alloc in leave_types:
            lt_res = await session.execute(
                select(LeaveType).where(LeaveType.tenant_id == tenant.id, LeaveType.code == lt_code)
            )
            lt = lt_res.scalar_one_or_none()
            if not lt:
                lt = LeaveType(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    organization_id=org.id,
                    code=lt_code,
                    name=lt_name,
                    is_paid=True,
                )
                session.add(lt)
                await session.flush()

            # Assign balance to Alex Morgan
            lb_res = await session.execute(
                select(LeaveBalance).where(
                    LeaveBalance.employee_id == alex_emp.id,
                    LeaveBalance.leave_type_id == lt.id,
                    LeaveBalance.fiscal_year == curr_year,
                )
            )
            if not lb_res.scalar_one_or_none():
                used = 2.0 if lt_code == "PAID" else 1.0 if lt_code == "SICK" else 0.0
                lb = LeaveBalance(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    organization_id=org.id,
                    employee_id=alex_emp.id,
                    leave_type_id=lt.id,
                    fiscal_year=curr_year,
                    allocated_days=total_alloc,
                    used_days=used,
                    pending_days=0.0,
                    carry_forward_days=0.0,
                    balance_days=total_alloc - used,
                )
                session.add(lb)
                await session.flush()

        # 9. Attendance 30-Day History for Alex Morgan
        today = date.today()
        for i in range(30):
            att_date = today - timedelta(days=i)
            # Skip Sundays as rest days
            if att_date.weekday() == 6:
                continue

            att_res = await session.execute(
                select(AttendanceRecord).where(
                    AttendanceRecord.employee_id == alex_emp.id,
                    AttendanceRecord.work_date == att_date,
                )
            )
            if not att_res.scalar_one_or_none():
                in_time = datetime.combine(att_date, time(9, 2), tzinfo=UTC)
                out_time = datetime.combine(att_date, time(18, 5), tzinfo=UTC)
                rec = AttendanceRecord(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    organization_id=org.id,
                    employee_id=alex_emp.id,
                    shift_id=shift.id,
                    work_date=att_date,
                    check_in_time=in_time,
                    check_out_time=out_time,
                    regular_hours=Decimal("8.0"),
                    overtime_hours=Decimal("1.0"),
                    status="PRESENT",
                )
                session.add(rec)
        await session.flush()

        # 10. CRM Leads
        leads_data = [
            ("Robert", "Langdon", "robert@harvard-symbology.edu", "Harvard Academia", "EXECUTIVE", "HOT", "DIRECT", 125000),
            ("Sarah", "Connor", "sconnor@cyberdyne-defense.mil", "Cyberdyne Systems", "DIRECTOR", "HOT", "REFERRAL", 240000),
            ("Gordon", "Gekko", "ggekko@wallstreet-capital.com", "Gekko & Co Holdings", "PARTNER", "WARM", "OUTBOUND", 85000),
        ]
        for f, l, em, comp, tit, rat, src, val in leads_data:
            ld_res = await session.execute(
                select(Lead).where(Lead.tenant_id == tenant.id, Lead.email == em)
            )
            if not ld_res.scalar_one_or_none():
                lead = Lead(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    organization_id=org.id,
                    first_name=f,
                    last_name=l,
                    email=em,
                    company_name=comp,
                    title=tit,
                    status="QUALIFIED",
                    rating=rat,
                    source=src,
                    estimated_value=Decimal(str(val)),
                )
                session.add(lead)
        await session.flush()

        # 11. CRM Accounts (Customers)
        acc_data = [
            ("Omni Consumer Products", "CORPORATE", "Robotics & Defense", "contact@ocp.com", "+1-555-019-2831", 150000),
            ("Cyberdyne Industries Global", "CORPORATE", "Advanced AI Computing", "info@cyberdyne.ai", "+1-555-012-9844", 300000),
            ("Weyland-Yutani Technologies", "CORPORATE", "Aerospace & Bio-Tech", "procurement@weyland.com", "+1-555-014-7721", 500000),
        ]
        cust_map: dict[str, Customer] = {}
        for cname, ctype, ind, cem, cph, cred in acc_data:
            c_res = await session.execute(
                select(Customer).where(Customer.tenant_id == tenant.id, Customer.name == cname)
            )
            cust = c_res.scalar_one_or_none()
            if not cust:
                cust = Customer(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    organization_id=org.id,
                    name=cname,
                    customer_type=ctype,
                    industry=ind,
                    email=cem,
                    phone=cph,
                    credit_limit=Decimal(str(cred)),
                    status="ACTIVE",
                )
                session.add(cust)
                await session.flush()
            cust_map[cname] = cust

        # 12. CRM Contacts
        contacts_data = [
            ("John", "Connor", "jconnor@cyberdyne.ai", "+1-555-011-2233", "Chief Technology Officer", "Engineering", "Cyberdyne Industries Global", True),
            ("Ellen", "Ripley", "ripley@weyland.com", "+1-555-018-4455", "VP Fleet Operations", "Logistics", "Weyland-Yutani Technologies", True),
            ("Richard", "Jones", "dick.jones@ocp.com", "+1-555-019-6677", "Senior VP Commercial", "Executive", "Omni Consumer Products", True),
        ]
        for f, l, em, ph, tit, dep, comp_name, is_p in contacts_data:
            ct_res = await session.execute(
                select(Contact).where(Contact.tenant_id == tenant.id, Contact.email == em)
            )
            if not ct_res.scalar_one_or_none():
                target_cust = cust_map[comp_name]
                ct = Contact(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    organization_id=org.id,
                    customer_id=target_cust.id,
                    first_name=f,
                    last_name=l,
                    email=em,
                    phone=ph,
                    title=tit,
                    department=dep,
                    is_primary=is_p,
                )
                session.add(ct)
        await session.flush()

        # 13. CRM Deals (Opportunities)
        deals_data = [
            ("Enterprise Cloud Migration", 125000, "NEGOTIATION", 80, "Cyberdyne Industries Global"),
            ("Autonomous Supply Chain Rollout", 240000, "PROPOSAL", 60, "Weyland-Yutani Technologies"),
            ("Vertex Copilot Enterprise License", 68000, "CLOSED_WON", 100, "Omni Consumer Products"),
        ]
        deal_map: dict[str, Deal] = {}
        for d_title, d_val, d_stg, d_prob, comp_name in deals_data:
            dl_res = await session.execute(
                select(Deal).where(Deal.tenant_id == tenant.id, Deal.title == d_title)
            )
            dl = dl_res.scalar_one_or_none()
            if not dl:
                target_cust = cust_map[comp_name]
                dl = Deal(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    organization_id=org.id,
                    customer_id=target_cust.id,
                    pipeline_id=uuid.uuid4(),
                    stage_id=uuid.uuid4(),
                    title=d_title,
                    value=Decimal(str(d_val)),
                    currency="USD",
                    win_probability_pct=Decimal(str(d_prob)),
                    status="WON" if d_stg == "CLOSED_WON" else "OPEN",
                )
                session.add(dl)
                await session.flush()
            deal_map[d_title] = dl

        # 14. Quotations & Sales Orders
        ocp_cust = cust_map["Omni Consumer Products"]
        q_res = await session.execute(
            select(Quotation).where(Quotation.tenant_id == tenant.id, Quotation.quotation_number == "QT-2026-001")
        )
        if not q_res.scalar_one_or_none():
            q = Quotation(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                organization_id=org.id,
                quotation_number="QT-2026-001",
                customer_id=ocp_cust.id,
                status="CONVERTED",
                subtotal=Decimal("60000.00"),
                tax_amount=Decimal("8000.00"),
                grand_total=Decimal("68000.00"),
                valid_until=today + timedelta(days=45),
            )
            session.add(q)
            await session.flush()

            q_item = QuotationItem(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                organization_id=org.id,
                quotation_id=q.id,
                sort_order=1,
                description="VertexERP AI Enterprise Annual License (100 seats)",
                quantity=Decimal("1.0"),
                unit_price=Decimal("60000.00"),
                discount_pct=Decimal("0.0"),
                tax_pct=Decimal("13.33"),
                line_total=Decimal("68000.00"),
            )
            session.add(q_item)

            # Corresponding confirmed sales order
            so = SalesOrder(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                organization_id=org.id,
                order_number="SO-2026-001",
                customer_id=ocp_cust.id,
                quotation_id=q.id,
                status="CONFIRMED",
                grand_total=Decimal("68000.00"),
            )
            session.add(so)
            await session.flush()

            so_item = SalesOrderItem(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                organization_id=org.id,
                sales_order_id=so.id,
                sort_order=1,
                description="VertexERP AI Enterprise Annual License (100 seats)",
                quantity=Decimal("1.0"),
                unit_price=Decimal("60000.00"),
                discount_pct=Decimal("0.0"),
                tax_pct=Decimal("13.33"),
                line_total=Decimal("68000.00"),
            )
            session.add(so_item)

        await session.commit()
        logger.info("Enterprise demo database seeding completed successfully!")
        print("\n" + "=" * 60)
        print("  VERTEXERP AI — ENTERPRISE DEMO DATA SEEDED")
        print("=" * 60)
        print("Tenant:       Apex Global Holdings (slug: 'apex')")
        print("Organization: Apex Commercial Enterprise (USD)")
        print("\nDemo Accounts (Password: DemoPassword123!):")
        print("  Super Admin:       admin@vertexerp.com")
        print("  HR Manager:        hr@vertexerp.com")
        print("  Sales Manager:     sales@vertexerp.com")
        print("  Finance Manager:   finance@vertexerp.com")
        print("  Employee (ESS):    employee@vertexerp.com")
        print("=" * 60 + "\n")
        await close_db_engine()


if __name__ == "__main__":
    asyncio.run(seed_enterprise_demo())
