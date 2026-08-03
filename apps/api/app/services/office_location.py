import uuid

from app.models.office_location import OfficeLocation
from app.repositories.office_location import OfficeLocationRepository
from app.schemas.office_location import OfficeLocationCreate, OfficeLocationUpdate
from app.services.base import BaseService


class OfficeLocationService(BaseService[OfficeLocation, OfficeLocationRepository]):
    def __init__(self, repository: OfficeLocationRepository):
        super().__init__(repository)
