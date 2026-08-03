import uuid

from fastapi import HTTPException, status

from app.models.role import Role
from app.repositories.permission import PermissionRepository
from app.repositories.role import RoleRepository
from app.schemas.role import RoleCreate, RoleUpdate
from app.services.base import BaseService


class RoleService(BaseService[Role, RoleRepository]):
    def __init__(self, repository: RoleRepository, permission_repo: PermissionRepository):
        super().__init__(repository)
        self.permission_repo = permission_repo

    async def create_role(self, obj_in: RoleCreate) -> Role:
        role_data = obj_in.model_dump(exclude={"permission_ids"})
        role = await self.repository.create(role_data)
        if obj_in.permission_ids:
            perms = []
            for pid in obj_in.permission_ids:
                p = await self.permission_repo.get(pid)
                if p:
                    perms.append(p)
            role.permissions = perms
            await self.repository.db.commit()
            await self.repository.db.refresh(role)
        return role

    async def update_role(self, role_id: uuid.UUID, obj_in: RoleUpdate) -> Role:
        role = await self.repository.get_with_permissions(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"permission_ids"})
        for field, val in update_data.items():
            setattr(role, field, val)

        if obj_in.permission_ids is not None:
            perms = []
            for pid in obj_in.permission_ids:
                p = await self.permission_repo.get(pid)
                if p:
                    perms.append(p)
            role.permissions = perms

        await self.repository.db.commit()
        await self.repository.db.refresh(role)
        return role

    async def get_by_org(self, org_id: uuid.UUID) -> list[Role]:
        return await self.repository.get_by_org_id(org_id)
