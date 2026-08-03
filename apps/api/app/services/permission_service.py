from app.models.permission import Permission
from app.repositories.permission import PermissionRepository
from app.services.base import BaseService


class PermissionService(BaseService[Permission, PermissionRepository]):
    def __init__(self, repository: PermissionRepository):
        super().__init__(repository)

    async def get_by_code(self, code: str) -> Permission | None:
        return await self.repository.get_by_code(code)
