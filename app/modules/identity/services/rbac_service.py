"""RBAC / ABAC permission evaluation service."""

import json
import uuid
from typing import Any

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_tenant_id
from app.core.permissions import PermissionCode, SystemRole
from app.modules.identity.models.role import Permission, RolePermission
from app.modules.identity.repositories.role_repository import RoleRepository


SYSTEM_ROLE_PERMISSIONS: dict[str, set[str]] = {
    SystemRole.TENANT_ADMIN.value: {p.value for p in PermissionCode},
    SystemRole.ORG_ADMIN.value: {
        p.value
        for p in PermissionCode
        if not p.value.startswith("audit:security_events")
        and p.value != PermissionCode.ORGANIZATION_DELETE.value
    },
    SystemRole.EXECUTIVE.value: {p.value for p in PermissionCode},
    "Administrator": {p.value for p in PermissionCode},
    "SystemAdmin": {p.value for p in PermissionCode},
    "Admin": {p.value for p in PermissionCode},
    SystemRole.CFO.value: {
        p.value
        for p in PermissionCode
        if p.value.startswith("finance:")
        or p.value.startswith("analytics:")
        or p.value.startswith("procurement:")
        or p.value.startswith("organization:")
    },
    SystemRole.SENIOR_ACCOUNTANT.value: {
        p.value
        for p in PermissionCode
        if p.value.startswith("finance:")
        or p.value.startswith("analytics:")
        or p.value.startswith("organization:")
    },
    SystemRole.PLANT_MANAGER.value: {
        p.value
        for p in PermissionCode
        if p.value.startswith("manufacturing:")
        or p.value.startswith("inventory:")
        or p.value.startswith("organization:")
    },
    SystemRole.PRODUCTION_PLANNER.value: {
        p.value
        for p in PermissionCode
        if p.value.startswith("manufacturing:")
        or p.value.startswith("inventory:")
        or p.value.startswith("organization:")
    },
    SystemRole.QUALITY_INSPECTOR.value: {
        p.value
        for p in PermissionCode
        if p.value.startswith("manufacturing:")
        or p.value.startswith("organization:")
    },
    SystemRole.MACHINE_OPERATOR.value: {
        p.value for p in PermissionCode if p.value.startswith("manufacturing:")
    },
    SystemRole.HR_MANAGER.value: {
        p.value
        for p in PermissionCode
        if p.value.startswith("hr:") or p.value.startswith("organization:")
    },
    SystemRole.PAYROLL_OFFICER.value: {
        p.value
        for p in PermissionCode
        if p.value.startswith("hr:payroll") or p.value.startswith("organization:")
    },
    SystemRole.SALES_MANAGER.value: {
        p.value
        for p in PermissionCode
        if p.value.startswith("crm:") or p.value.startswith("organization:")
    },
    SystemRole.SALES_REPRESENTATIVE.value: {
        p.value
        for p in PermissionCode
        if p.value.startswith("crm:") or p.value.startswith("organization:")
    },
    SystemRole.INVENTORY_MANAGER.value: {
        p.value
        for p in PermissionCode
        if p.value.startswith("inventory:")
        or p.value.startswith("procurement:")
        or p.value.startswith("organization:")
    },
    SystemRole.PROCUREMENT_OFFICER.value: {
        p.value
        for p in PermissionCode
        if p.value.startswith("procurement:")
        or p.value.startswith("inventory:")
        or p.value.startswith("organization:")
    },
    SystemRole.WAREHOUSE_OPERATOR.value: {
        p.value
        for p in PermissionCode
        if p.value.startswith("inventory:") or p.value.startswith("organization:")
    },
    SystemRole.BUSINESS_ANALYST.value: {
        p.value
        for p in PermissionCode
        if p.value.startswith("analytics:") or p.value.startswith("organization:")
    },
    SystemRole.AUDITOR.value: {
        p.value
        for p in PermissionCode
        if p.value.startswith("audit:") or p.value.endswith(":read")
    },
    SystemRole.STANDARD_USER.value: {
        PermissionCode.ORGANIZATION_READ.value,
        PermissionCode.IDENTITY_USERS_READ.value,
    },
}


class RbacService:
    """Service for evaluating user roles and effective granular permissions."""

    def __init__(self, session: AsyncSession, redis: Redis | None = None) -> None:
        self.session = session
        self.redis = redis
        self.role_repo = RoleRepository(session)

    async def get_user_roles_and_permissions(
        self,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        tenant_id: uuid.UUID | None = None,
        roles: list[str] | None = None,
    ) -> tuple[list[str], list[str]]:
        """
        Calculates all active role codes and distinct permission strings
        for a user within an active organization context.
        Caches result in Redis using tenant-isolated key when Redis is available.
        """
        effective_tenant_id = tenant_id or get_tenant_id()
        cache_key = (
            f"rbac:perms:{effective_tenant_id}:{user_id}:{organization_id}"
            if effective_tenant_id
            else f"rbac:perms:{user_id}:{organization_id}"
        )

        if self.redis:
            try:
                cached_raw = await self.redis.get(cache_key)
                if cached_raw:
                    cached_data = json.loads(
                        cached_raw.decode("utf-8") if isinstance(cached_raw, bytes) else cached_raw
                    )
                    return cached_data.get("roles", []), cached_data.get("permissions", [])
            except Exception:
                pass

        user_roles_data = await self.role_repo.get_user_roles(user_id, organization_id)
        role_codes: list[str] = []
        role_ids: list[uuid.UUID] = []

        for _user_role, role in user_roles_data:
            role_codes.append(role.code)
            role_ids.append(role.id)

        # Fallback to roles parameter if user has no DB user_role mappings
        if not role_codes and roles:
            role_codes.extend(roles)

        permission_codes: set[str] = set()
        if role_ids:
            stmt = (
                select(Permission.code)
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .where(RolePermission.role_id.in_(role_ids))
                .distinct()
            )
            result = await self.session.execute(stmt)
            permission_codes.update(result.scalars().all())

        # Merge standard system permissions for recognized system roles
        for r in role_codes:
            if r in SYSTEM_ROLE_PERMISSIONS:
                permission_codes.update(SYSTEM_ROLE_PERMISSIONS[r])

        sorted_perms = sorted(permission_codes)

        if self.redis:
            try:
                payload = json.dumps({"roles": role_codes, "permissions": sorted_perms})
                await self.redis.set(cache_key, payload, ex=300)
            except Exception:
                pass

        return role_codes, sorted_perms

    async def has_permission(
        self,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        required_permission: str,
        tenant_id: uuid.UUID | None = None,
    ) -> bool:
        """Evaluates whether user has the required permission code."""
        _, perms = await self.get_user_roles_and_permissions(
            user_id, organization_id, tenant_id=tenant_id
        )
        return required_permission in perms

    async def invalidate_user_cache(
        self,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        tenant_id: uuid.UUID | None = None,
    ) -> None:
        """Invalidates cached RBAC permissions for a user within an organization context."""
        if not self.redis:
            return
        effective_tenant_id = tenant_id or get_tenant_id()
        cache_key = (
            f"rbac:perms:{effective_tenant_id}:{user_id}:{organization_id}"
            if effective_tenant_id
            else f"rbac:perms:{user_id}:{organization_id}"
        )
        try:
            await self.redis.delete(cache_key)
        except Exception:
            pass
