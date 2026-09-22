"""Location service."""

import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.modules.organization.models.location import Location
from app.modules.organization.repositories.location_repository import LocationRepository
from app.modules.organization.schemas.location import LocationCreate, LocationUpdate


class LocationService:
    """Business service for Location site/facility management."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.loc_repo = LocationRepository(session)

    async def create_location(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: LocationCreate
    ) -> Location:
        existing = await self.loc_repo.get_by_code(data.code, tenant_id, org_id)
        if existing:
            raise ConflictException(
                f"Location with code '{data.code}' already exists in this organization"
            )

        loc = Location(
            tenant_id=tenant_id,
            organization_id=org_id,
            branch_id=data.branch_id,
            code=data.code,
            name=data.name,
            location_type=data.location_type,
            address_line1=data.address_line1,
            address_line2=data.address_line2,
            city=data.city,
            state=data.state,
            postal_code=data.postal_code,
            country=data.country,
            latitude=data.latitude,
            longitude=data.longitude,
            is_active=data.is_active,
        )
        return await self.loc_repo.create(loc)

    async def get_location(
        self, loc_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Location:
        loc = await self.loc_repo.get_by_id(loc_id, tenant_id, org_id)
        if not loc:
            raise NotFoundException(f"Location '{loc_id}' not found")
        return loc

    async def list_locations(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[Location]:
        return await self.loc_repo.list_by_org(tenant_id, org_id, is_active)

    async def update_location(
        self, loc_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, data: LocationUpdate
    ) -> Location:
        loc = await self.get_location(loc_id, tenant_id, org_id)

        if data.code is not None and data.code != loc.code:
            existing = await self.loc_repo.get_by_code(data.code, tenant_id, org_id)
            if existing and existing.id != loc.id:
                raise ConflictException(f"Location with code '{data.code}' already exists")
            loc.code = data.code

        if data.name is not None:
            loc.name = data.name
        if data.location_type is not None:
            loc.location_type = data.location_type
        if data.branch_id is not None:
            loc.branch_id = data.branch_id
        if data.address_line1 is not None:
            loc.address_line1 = data.address_line1
        if data.address_line2 is not None:
            loc.address_line2 = data.address_line2
        if data.city is not None:
            loc.city = data.city
        if data.state is not None:
            loc.state = data.state
        if data.postal_code is not None:
            loc.postal_code = data.postal_code
        if data.country is not None:
            loc.country = data.country
        if data.latitude is not None:
            loc.latitude = data.latitude
        if data.longitude is not None:
            loc.longitude = data.longitude
        if data.is_active is not None:
            loc.is_active = data.is_active

        return await self.loc_repo.update(loc)

    async def delete_location(
        self, loc_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> None:
        loc = await self.get_location(loc_id, tenant_id, org_id)
        await self.loc_repo.soft_delete(loc)
