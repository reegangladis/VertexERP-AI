from app.models.permission import Permission
from app.repositories.permission import PermissionRepository
from app.services.base import BaseService


class PermissionService(BaseService[Permission, PermissionRepository]):
    def __init__(self, repository: PermissionRepository):
        super().__init__(repository)

    async def get_by_name(self, name: str) -> Permission | None:
        return await self.repository.get_by_name(name)

    async def seed_default_permissions(self) -> None:
        # Predefined permission sets
        default_permissions = [
            # Users permissions
            {
                "name": "users.read",
                "description": "View user accounts",
                "category": "users",
            },
            {
                "name": "users.create",
                "description": "Create new users",
                "category": "users",
            },
            {
                "name": "users.update",
                "description": "Modify user parameters",
                "category": "users",
            },
            {
                "name": "users.delete",
                "description": "Soft-delete user accounts",
                "category": "users",
            },
            # Roles permissions
            {
                "name": "roles.read",
                "description": "View system roles",
                "category": "roles",
            },
            {
                "name": "roles.manage",
                "description": "Configure roles and permissions",
                "category": "roles",
            },
            # HR & CRM placeholders
            {"name": "hr.read", "description": "View HR operations", "category": "hr"},
            {
                "name": "finance.update",
                "description": "Modify finance accounts",
                "category": "finance",
            },
            {
                "name": "inventory.manage",
                "description": "Track stock levels",
                "category": "inventory",
            },
            # General Admin
            {
                "name": "admin.full",
                "description": "Root administrator privilege",
                "category": "admin",
            },
        ]

        for perm_in in default_permissions:
            existing = await self.repository.get_by_name(perm_in["name"])
            if not existing:
                await self.repository.create(perm_in)
