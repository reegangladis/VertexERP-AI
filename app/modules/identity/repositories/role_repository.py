"""Repository for Roles, Permissions, and RBAC UserRole assignments."""

import uuid
from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.models.role import Permission, Role, RolePermission, UserRole


class RoleRepository:
    """Data access repository for Roles, Permissions, and UserRole mappings."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_role_by_id(self, role_id: uuid.UUID, tenant_id: uuid.UUID) -> Role | None:
        stmt = select(Role).where(
            Role.id == role_id, Role.tenant_id == tenant_id, Role.is_deleted.is_(False)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_role_by_code(self, code: str, tenant_id: uuid.UUID) -> Role | None:
        stmt = select(Role).where(
            Role.code == code, Role.tenant_id == tenant_id, Role.is_deleted.is_(False)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_roles_by_tenant(self, tenant_id: uuid.UUID) -> Sequence[Role]:
        stmt = (
            select(Role)
            .where(Role.tenant_id == tenant_id, Role.is_deleted.is_(False))
            .order_by(Role.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_role(self, role: Role) -> Role:
        self.session.add(role)
        await self.session.flush()
        return role

    async def get_all_permissions(self) -> Sequence[Permission]:
        stmt = select(Permission).order_by(Permission.domain.asc(), Permission.code.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_permission_by_code(self, code: str) -> Permission | None:
        stmt = select(Permission).where(Permission.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_permission(self, permission: Permission) -> Permission:
        self.session.add(permission)
        await self.session.flush()
        return permission

    async def assign_permissions_to_role(
        self, tenant_id: uuid.UUID, role_id: uuid.UUID, permission_ids: list[uuid.UUID]
    ) -> None:
        # Clear existing mappings
        await self.session.execute(delete(RolePermission).where(RolePermission.role_id == role_id))
        for perm_id in permission_ids:
            mapping = RolePermission(
                tenant_id=tenant_id,
                role_id=role_id,
                permission_id=perm_id,
            )
            self.session.add(mapping)
        await self.session.flush()

    async def get_permissions_for_role(self, role_id: uuid.UUID) -> Sequence[Permission]:
        stmt = (
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == role_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def assign_user_role(self, user_role: UserRole) -> UserRole:
        self.session.add(user_role)
        await self.session.flush()
        return user_role

    async def get_user_roles(
        self, user_id: uuid.UUID, organization_id: uuid.UUID
    ) -> Sequence[tuple[UserRole, Role]]:
        stmt = (
            select(UserRole, Role)
            .join(Role, Role.id == UserRole.role_id)
            .where(
                UserRole.user_id == user_id,
                UserRole.organization_id == organization_id,
                Role.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.tuples().all()
