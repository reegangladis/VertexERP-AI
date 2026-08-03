import uuid

from app.models.location import Location
from app.repositories.location import LocationRepository
from app.services.base import BaseService


class LocationService(BaseService[Location, LocationRepository]):
    def __init__(self, repository: LocationRepository):
        super().__init__(repository)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Location]:
        return await self.repository.get_by_org_id(org_id)
