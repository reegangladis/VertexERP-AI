import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.role import Role
from app.models.permission import Permission

class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: AsyncSession):
        super().__init__(Role, db)

    async def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name, Role.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_roles_by_org(self, organization_id: uuid.UUID | None) -> list[Role]:
        # Fetch organization specific roles + default global roles
        stmt = select(Role).where(
            (Role.organization_id == organization_id) | (Role.organization_id == None),
            Role.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def ensure_default_roles(self, organization_id: uuid.UUID | None = None) -> dict[str, Role]:
        """Ensure standard enterprise RBAC roles exist in DB, creating them if missing."""
        standard_roles = [
            ("Super Admin", "Full system platform administrator access"),
            ("Organization Admin", "Full organization tenant administrator access"),
            ("HR Manager", "Human resources, employee, leave, and payroll access"),
            ("Finance Manager", "Accounting, invoices, budgets, and chart of accounts access"),
            ("CRM Manager", "Customer relations, leads, deals, and support access"),
            ("Inventory Manager", "Products, warehouses, purchase orders, and stock access"),
            ("Manufacturing Manager", "BOM, routings, work centers, and shop floor access"),
            ("Employee", "Standard employee workspace access"),
            ("Viewer", "Read-only workspace access"),
        ]

        roles_map: dict[str, Role] = {}
        for name, desc in standard_roles:
            stmt = select(Role).where(Role.name == name, Role.is_deleted == False)
            if organization_id:
                stmt = stmt.where((Role.organization_id == organization_id) | (Role.organization_id == None))
            res = await self.db.execute(stmt)
            role_obj = res.scalar_one_or_none()

            if not role_obj:
                role_obj = Role(
                    name=name,
                    description=desc,
                    organization_id=organization_id,
                    is_system=True
                )
                self.db.add(role_obj)
                await self.db.flush()

            roles_map[name] = role_obj

        await self.db.commit()
        return roles_map
