from typing import Any, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository[ModelType: Base]:
    """Base class for database operations implementing the Repository Pattern."""

    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: Any) -> ModelType | None:
        """Retrieves a single record by primary key."""
        return await self.db.get(self.model, id)

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Retrieves multiple records with support for offset/limit pagination."""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj_in: Any) -> ModelType:
        """Saves a new model instance to the database."""
        self.db.add(obj_in)
        await self.db.commit()
        await self.db.refresh(obj_in)
        return obj_in

    async def delete(self, id: Any) -> ModelType | None:
        """Removes a model instance from the database."""
        obj = await self.get(id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
        return obj
