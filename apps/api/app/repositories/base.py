from typing import Any

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base


class BaseRepository[ModelType: Base]:
    """Base class for database operations implementing the Repository Pattern."""

    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: Any) -> ModelType | None:
        """Retrieves a single record by primary key."""
        stmt = select(self.model).where(self.model.id == id)
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Retrieves multiple records with support for pagination (sprint 1.1 compatible)."""
        stmt = select(self.model)
        if hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted == False)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        sort: list[str] | None = None,
        include_deleted: bool = False,
    ) -> tuple[list[ModelType], int]:
        """Retrieves multiple records with dynamic filtering, sorting, pagination, and soft delete checks."""
        stmt = select(self.model)

        # Filter out soft-deleted records by default
        if hasattr(self.model, "is_deleted") and not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)

        # Dynamic filtering
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    stmt = stmt.where(getattr(self.model, field) == value)

        # Count total records before pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar_one()

        # Dynamic sorting
        if sort:
            for sort_field in sort:
                descending = sort_field.startswith("-")
                field_name = sort_field.lstrip("-")
                if hasattr(self.model, field_name):
                    column = getattr(self.model, field_name)
                    stmt = stmt.order_by(desc(column) if descending else asc(column))
        else:
            # Default sorting by created_at if available
            if hasattr(self.model, "created_at"):
                stmt = stmt.order_by(desc(self.model.created_at))

        # Pagination
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total_count

    async def create(self, obj_in: Any) -> ModelType:
        """Saves a new model instance or creates it from a dictionary/schema."""
        if isinstance(obj_in, self.model):
            db_obj = obj_in
        else:
            if hasattr(obj_in, "model_dump"):
                obj_data = obj_in.model_dump()
            elif isinstance(obj_in, dict):
                obj_data = obj_in
            else:
                obj_data = dict(obj_in)

            valid_keys = {c.key for c in self.model.__table__.columns}
            filtered_data = {k: v for k, v in obj_data.items() if k in valid_keys}
            db_obj = self.model(**filtered_data)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: Any) -> ModelType:
        """Updates an existing database record with the provided parameters."""
        db_obj = await self.db.merge(db_obj)
        if hasattr(obj_in, "model_dump"):
            update_data = obj_in.model_dump(exclude_unset=True)
        elif isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = dict(obj_in)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: Any, hard: bool = False) -> ModelType | None:
        """Removes a model instance from the database (supports soft delete)."""
        obj = await self.db.get(self.model, id)
        if not obj:
            return None

        if not hard and hasattr(obj, "soft_delete"):
            obj.soft_delete()
            self.db.add(obj)
        else:
            await self.db.delete(obj)

        await self.db.commit()
        return obj
