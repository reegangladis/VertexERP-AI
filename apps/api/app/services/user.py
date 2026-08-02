from datetime import UTC, datetime, timedelta

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user import PasswordHistoryRepository, UserRepository
from app.services.base import BaseService


class UserService(BaseService[User, UserRepository]):
    def __init__(
        self,
        repository: UserRepository,
        password_history_repo: PasswordHistoryRepository,
    ):
        super().__init__(repository)
        self.password_history_repo = password_history_repo

    async def get_by_email(self, email: str) -> User | None:
        return await self.repository.get_by_email(email)

    async def get_by_username(self, username: str) -> User | None:
        return await self.repository.get_by_username(username)

    async def create_user(self, user_in: dict) -> User:
        clear_pwd = user_in.pop("password")
        pwd_hash = hash_password(clear_pwd)
        user_in["password_hash"] = pwd_hash

        user = await self.repository.create(user_in)

        # Log to password history
        await self.password_history_repo.create(
            {"user_id": user.id, "password_hash": pwd_hash}
        )

        return user

    async def update_password(self, user: User, new_password: str) -> User:
        pwd_hash = hash_password(new_password)

        # Verify password history constraints (not matching last 3 passwords)
        history = await self.password_history_repo.get_history_by_user(user.id)
        for old_pwd in history[:3]:
            if verify_password(new_password, old_pwd.password_hash):
                raise ValueError(
                    "Password matches one of your last 3 passwords. Please choose another."
                )

        user.password_hash = pwd_hash
        updated = await self.repository.update(user, {"password_hash": pwd_hash})

        # Log new password history record
        await self.password_history_repo.create(
            {"user_id": user.id, "password_hash": pwd_hash}
        )

        return updated

    async def increment_failed_attempts(
        self, user: User, threshold: int = 5, duration_minutes: int = 15
    ) -> User:
        user.failed_login_attempts += 1
        update_dict = {"failed_login_attempts": user.failed_login_attempts}

        if user.failed_login_attempts >= threshold:
            user.locked_until = datetime.now(UTC) + timedelta(minutes=duration_minutes)
            update_dict["locked_until"] = user.locked_until
            update_dict["status"] = "locked"

        return await self.repository.update(user, update_dict)

    async def reset_failed_attempts(self, user: User) -> User:
        update_dict = {"failed_login_attempts": 0, "locked_until": None}
        if user.status == "locked":
            update_dict["status"] = "active"
        return await self.repository.update(user, update_dict)

    async def is_account_locked(self, user: User) -> bool:
        if user.locked_until:
            if user.locked_until > datetime.now(UTC):
                return True
            # Lock has expired, reset attempts
            await self.reset_failed_attempts(user)
        return False
