"""Location repository."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organization.models.location import Location


class LocationRepository:
    """Repository for Location persistence with strict tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, loc_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Location | None:
        stmt = select(Location).where(
            Location.id == loc_id,
            Location.tenant_id == tenant_id,
            Location.organization_id == org_id,
            Location.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Location | None:
        stmt = select(Location).where(
            Location.code == code,
            Location.tenant_id == tenant_id,
            Location.organization_id == org_id,
            Location.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[Location]:
        stmt = select(Location).where(
            Location.tenant_id == tenant_id,
            Location.organization_id == org_id,
            Location.is_deleted.is_(False),
        )
        if is_active is not None:
            stmt = stmt.where(Location.is_active.is_(is_active))
        stmt = stmt.order_by(Location.name.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, loc: Location) -> Location:
        self.session.add(loc)
        await self.session.flush()
        return loc

    async def update(self, loc: Location) -> Location:
        loc.updated_at = datetime.now(UTC)
        loc.version += 1
        await self.session.flush()
        return loc

    async def soft_delete(self, loc: Location) -> None:
        loc.is_deleted = True
        loc.deleted_at = datetime.now(UTC)
        loc.version += 1
        await self.session.flush()
