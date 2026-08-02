from typing import Any, TypeVar

from app.database.base import Base
from app.repositories.base import BaseRepository

ModelType = TypeVar("ModelType", bound=Base)
RepoType = TypeVar("RepoType", bound=BaseRepository)


class BaseService[ModelType: Base, RepoType: BaseRepository]:
    """Base class for service layer components wrapping a repository."""

    def __init__(self, repository: RepoType) -> None:
        self.repository = repository

    async def get(self, id: Any) -> ModelType | None:
        """Retrieves a single record by its primary key ID."""
        return await self.repository.get(id)

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        sort: list[str] | None = None,
    ) -> tuple[list[ModelType], int]:
        """Retrieves multiple records with support for filtering and sorting."""
        return await self.repository.get_multi(
            skip=skip, limit=limit, filters=filters, sort=sort
        )

    async def create(self, obj_in: Any) -> ModelType:
        """Standardized record creation with service validation checks."""
        await self.validate_create(obj_in)
        return await self.repository.create(obj_in)

    async def update(self, id: Any, obj_in: Any) -> ModelType | None:
        """Standardized record update with service validation checks."""
        db_obj = await self.get(id)
        if not db_obj:
            return None
        await self.validate_update(db_obj, obj_in)
        return await self.repository.update(db_obj, obj_in)

    async def delete(self, id: Any, hard: bool = False) -> ModelType | None:
        """Standardized record deletion (soft or hard)."""
        await self.validate_delete(id)
        return await self.repository.delete(id, hard=hard)

    async def validate_create(self, obj_in: Any) -> None:
        """Pre-create validation hook.

        Override in subclasses to enforce module rules.
        """
        pass

    async def validate_update(self, db_obj: ModelType, obj_in: Any) -> None:
        """Pre-update validation hook.

        Override in subclasses to enforce module rules.
        """
        pass

    async def validate_delete(self, id: Any) -> None:
        """Pre-delete validation hook.

        Override in subclasses to enforce module rules.
        """
        pass
