import uuid

from app.models.branch import Branch
from app.repositories.branch import BranchRepository
from app.services.base import BaseService


class BranchService(BaseService[Branch, BranchRepository]):
    def __init__(self, repository: BranchRepository):
        super().__init__(repository)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Branch]:
        return await self.repository.get_by_org_id(org_id)
