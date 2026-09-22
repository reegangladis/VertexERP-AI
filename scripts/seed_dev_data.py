"""Database Seeding Script for VertexERP AI V2 Development Environment.

Usage:
    python scripts/seed_dev_data.py
"""

import asyncio
import sys
import uuid

from sqlalchemy import select

from app.core.logging import logger, setup_logging
from app.core.security import hash_password
from app.infrastructure.database.session import async_session_factory, engine
from app.modules.hr.models.employee import Employee
from app.modules.identity.models.role import UserRole
from app.modules.identity.models.user import User
from app.modules.identity.models.user_credential import UserCredential
from app.modules.identity.services.auth_service import AuthService
from app.modules.inventory.models.category import ProductCategory
from app.modules.inventory.models.product import Product
from app.modules.inventory.models.uom import UnitOfMeasure
from app.modules.inventory.models.warehouse import Warehouse
from app.modules.organization.models.branch import Branch
from app.modules.organization.models.department import Department
from app.modules.organization.models.location import Location
from app.modules.organization.models.organization import Organization
from app.modules.organization.models.tenant import Tenant
from app.modules.procurement.models.supplier import Supplier


async def seed_data() -> None:
    setup_logging()
    logger.info("Starting VertexERP AI V2 development database seeding...")

    async with async_session_factory() as session:
        # 1. Check if demo tenant already exists
        result = await session.execute(select(Tenant).where(Tenant.slug == "vertex"))
        existing_tenant = result.scalar_one_or_none()

        if existing_tenant:
            logger.info("Demo tenant 'vertex' already exists. Skipping duplicate seed.")
            return

        # 2. Provision Tenant and Organization
        tenant = Tenant(
            id=uuid.uuid4(),
            name="Vertex Enterprises Global",
            slug="vertex",
            is_active=True,
        )
        session.add(tenant)
        await session.flush()

        org = Organization(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            name="Vertex Global Operations",
            legal_name="Vertex Enterprises Inc.",
            tax_identifier="US-999888777",
            base_currency="USD",
            is_active=True,
        )
        session.add(org)
        await session.flush()

        # 3. Seed Roles and Permissions for this Tenant
        auth_service = AuthService(session)
        admin_role, org_admin_role, auditor_role, user_role = (
            await auth_service._seed_system_permissions_and_roles(tenant.id)
        )

        # 4. Provision Root Administrator
        admin_user = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="admin@vertexerp.io",
            full_name="System Administrator",
            is_active=True,
            is_verified=True,
            default_organization_id=org.id,
        )
        session.add(admin_user)
        await session.flush()

        admin_creds = UserCredential(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            user_id=admin_user.id,
            password_hash=hash_password("Password123!"),
            salt="dev_salt_12345",
        )
        session.add(admin_creds)

        # Assign Admin Role
        admin_user_role = UserRole(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            user_id=admin_user.id,
            role_id=admin_role.id,
            organization_id=org.id,
        )
        session.add(admin_user_role)

        # Add Tenant Membership
        await auth_service.org_service.add_membership(
            tenant_id=tenant.id,
            user_id=admin_user.id,
            org_id=org.id,
            is_default=True,
        )

        # 5. Provision Standard Demo User
        demo_user = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="user@vertexerp.io",
            full_name="Demo Operations User",
            is_active=True,
            is_verified=True,
            default_organization_id=org.id,
        )
        session.add(demo_user)
        await session.flush()

        demo_creds = UserCredential(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            user_id=demo_user.id,
            password_hash=hash_password("Password123!"),
            salt="dev_salt_67890",
        )
        session.add(demo_creds)

        demo_user_role = UserRole(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            user_id=demo_user.id,
            role_id=user_role.id,
            organization_id=org.id,
        )
        session.add(demo_user_role)

        await auth_service.org_service.add_membership(
            tenant_id=tenant.id,
            user_id=demo_user.id,
            org_id=org.id,
            is_default=True,
        )

        # 6. Master Data: Locations, Branches, Departments
        loc_hq = Location(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            organization_id=org.id,
            code="LOC-HQ",
            name="San Francisco Corporate Campus",
            country="United States",
            state="CA",
            city="San Francisco",
            is_active=True,
        )
        session.add(loc_hq)
        await session.flush()

        branch_hq = Branch(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            organization_id=org.id,
            code="BR-SF",
            name="San Francisco Main Hub",
            is_headquarters=True,
            is_active=True,
        )
        session.add(branch_hq)
        await session.flush()

        dept_eng = Department(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            organization_id=org.id,
            branch_id=branch_hq.id,
            code="DEPT-ENG",
            name="AI & Engineering",
            is_active=True,
        )
        dept_ops = Department(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            organization_id=org.id,
            branch_id=branch_hq.id,
            code="DEPT-OPS",
            name="Supply Chain & Operations",
            is_active=True,
        )
        session.add_all([dept_eng, dept_ops])
        await session.flush()

        # 7. HR Employees
        emp_1 = Employee(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            organization_id=org.id,
            department_id=dept_eng.id,
            employee_number="EMP-1001",
            first_name="Alex",
            last_name="Mercer",
            email="alex.mercer@vertexerp.io",
            is_active=True,
        )
        emp_2 = Employee(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            organization_id=org.id,
            department_id=dept_ops.id,
            employee_number="EMP-1002",
            first_name="Elena",
            last_name="Rostova",
            email="elena.rostova@vertexerp.io",
            is_active=True,
        )
        session.add_all([emp_1, emp_2])

        # 8. Inventory UOMs, Categories, Warehouses, Products
        uom_ea = UnitOfMeasure(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            organization_id=org.id,
            code="EA",
            name="Each",
            is_active=True,
        )
        uom_kg = UnitOfMeasure(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            organization_id=org.id,
            code="KG",
            name="Kilogram",
            is_active=True,
        )
        session.add_all([uom_ea, uom_kg])
        await session.flush()

        cat_electronics = ProductCategory(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            organization_id=org.id,
            code="CAT-ELEC",
            name="Industrial Electronics",
            is_active=True,
        )
        cat_materials = ProductCategory(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            organization_id=org.id,
            code="CAT-RAW",
            name="Raw Materials",
            is_active=True,
        )
        session.add_all([cat_electronics, cat_materials])
        await session.flush()

        wh_main = Warehouse(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            organization_id=org.id,
            branch_id=branch_hq.id,
            code="WH-MAIN-01",
            name="Central Distribution Warehouse",
            is_active=True,
        )
        session.add(wh_main)
        await session.flush()

        prod_1 = Product(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            organization_id=org.id,
            category_id=cat_electronics.id,
            default_uom_id=uom_ea.id,
            sku="VTX-SRV-01",
            name="AI Edge Server Module 400W",
            description="High performance edge computing unit with onboard NPU",
            is_active=True,
        )
        prod_2 = Product(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            organization_id=org.id,
            category_id=cat_materials.id,
            default_uom_id=uom_kg.id,
            sku="VTX-ALU-6061",
            name="Aerospace Grade Aluminum Alloy 6061",
            description="Precision milled billet stock for CNC manufacturing",
            is_active=True,
        )
        session.add_all([prod_1, prod_2])

        # 9. Procurement Suppliers
        sup_1 = Supplier(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            organization_id=org.id,
            code="SUP-NV",
            name="Nvidia Microelectronics Corp",
            contact_email="procurement@nvidia-demo.io",
            is_active=True,
        )
        sup_2 = Supplier(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            organization_id=org.id,
            code="SUP-AL",
            name="Alcoa Industrial Alloys Ltd",
            contact_email="orders@alcoa-demo.io",
            is_active=True,
        )
        session.add_all([sup_1, sup_2])

        await session.commit()
        logger.info(
            "Seeding completed successfully! Demo credentials:\n"
            "--------------------------------------------------\n"
            "Email:    admin@vertexerp.io\n"
            "Password: Password123!\n"
            "Tenant:   vertex (optional)\n"
            "--------------------------------------------------"
        )


if __name__ == "__main__":
    asyncio.run(seed_data())
