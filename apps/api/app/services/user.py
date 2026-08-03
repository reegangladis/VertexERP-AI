import uuid

from fastapi import HTTPException, status

from app.core.security import hash_password
from app.models.user import User
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import BaseService


class UserService(BaseService[User, UserRepository]):
    def __init__(self, repository: UserRepository, role_repo: RoleRepository):
        super().__init__(repository)
        self.role_repo = role_repo

    async def create_user(self, obj_in: UserCreate) -> User:
        existing_email = await self.repository.get_by_email(obj_in.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered",
            )
        existing_username = await self.repository.get_by_username(obj_in.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is already taken",
            )

        data = obj_in.model_dump(exclude={"role_ids", "password"})
        data["password_hash"] = hash_password(obj_in.password)

        user = await self.repository.create(data)
        if obj_in.role_ids:
            await self.repository.assign_roles(user, obj_in.role_ids)

        return await self.repository.get_with_roles(user.id) or user

    async def update_user(self, user_id: uuid.UUID, obj_in: UserUpdate) -> User:
        user = await self.repository.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        update_data = obj_in.model_dump(exclude_unset=True, exclude={"role_ids"})
        for k, v in update_data.items():
            setattr(user, k, v)

        if obj_in.role_ids is not None:
            await self.repository.assign_roles(user, obj_in.role_ids)

        await self.repository.db.commit()
        return await self.repository.get_with_roles(user_id) or user

    async def get_user_with_roles(self, user_id: uuid.UUID) -> User:
        user = await self.repository.get_with_roles(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user
