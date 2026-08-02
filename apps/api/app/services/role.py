import uuid

from app.models.role import Role
from app.repositories.permission import PermissionRepository
from app.repositories.role import RoleRepository
from app.services.base import BaseService


class RoleService(BaseService[Role, RoleRepository]):
    def __init__(
        self, repository: RoleRepository, permission_repo: PermissionRepository
    ):
        super().__init__(repository)
        self.permission_repo = permission_repo

    async def get_by_name(self, name: str) -> Role | None:
        return await self.repository.get_by_name(name)

    async def get_roles_by_org(self, organization_id: uuid.UUID | None) -> list[Role]:
        return await self.repository.get_roles_by_org(organization_id)

    async def assign_permissions_to_role(
        self, role_id: uuid.UUID, permission_names: list[str]
    ) -> Role | None:
        role = await self.repository.get(role_id)
        if not role:
            return None

        permissions = await self.permission_repo.get_by_names(permission_names)
        role.permissions = permissions

        self.repository.db.add(role)
        await self.repository.db.commit()
        await self.repository.db.refresh(role)
        return role

    async def seed_default_roles(self) -> None:
        # Predefined default system roles
        default_roles = [
            {
                "name": "Super Admin",
                "description": "Global administrator with full override permissions",
            },
            {
                "name": "Organization Admin",
                "description": "Tenant administrator managing an organization",
            },
            {
                "name": "Manager",
                "description": "Team lead overseeing users and metrics",
            },
            {"name": "HR", "description": "Human Resources officer"},
            {"name": "Finance", "description": "Accountant managing finances"},
            {"name": "Inventory", "description": "Stock supervisor tracking items"},
            {"name": "Sales", "description": "Sales agent"},
            {"name": "Employee", "description": "General staff worker"},
            {"name": "Viewer", "description": "Read-only auditor"},
        ]

        for role_in in default_roles:
            existing = await self.repository.get_by_name(role_in["name"])
            if not existing:
                await self.repository.create(role_in)
