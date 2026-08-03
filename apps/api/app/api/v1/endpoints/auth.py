from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db_session
from app.models.user import User
from app.repositories.login_history import LoginHistoryRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.role import RoleRepository
from app.repositories.session import RefreshTokenRepository, SessionRepository
from app.repositories.token import (
    EmailVerificationTokenRepository,
    PasswordResetTokenRepository,
)
from app.repositories.user import UserRepository
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.schemas.user import UserResponse, UserUpdate, UserWithRolesResponse
from app.services.auth import AuthService
from app.services.user import UserService

router = APIRouter()


def get_auth_service(db: AsyncSession = Depends(get_db_session)) -> AuthService:
    return AuthService(
        UserRepository(db),
        OrganizationRepository(db),
        RoleRepository(db),
        SessionRepository(db),
        RefreshTokenRepository(db),
        LoginHistoryRepository(db),
        EmailVerificationTokenRepository(db),
        PasswordResetTokenRepository(db),
    )


def get_user_service(db: AsyncSession = Depends(get_db_session)) -> UserService:
    return UserService(UserRepository(db), RoleRepository(db))


@router.post("/register", response_model=UserWithRolesResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    ip_address = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "Unknown")
    return await auth_service.login(data, ip_address=ip_address, user_agent=user_agent)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.refresh_tokens(data)


@router.post("/logout")
async def logout(
    data: RefreshTokenRequest | None = None,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    raw_token = data.refresh_token if data else None
    await auth_service.logout(current_user.id, raw_token)
    return {"message": "Logged out successfully"}


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.change_password(current_user.id, data)
    return {"message": "Password updated successfully"}


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    token = await auth_service.forgot_password(data.email)
    return {"message": "Password reset email sent if account exists", "token": token}


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.reset_password(data.token, data.new_password)
    return {"message": "Password reset successfully"}


@router.post("/verify-email")
async def verify_email(
    data: VerifyEmailRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.verify_email(data.token)
    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification():
    return {"message": "Verification email resent"}


@router.get("/me", response_model=UserWithRolesResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.patch("/me", response_model=UserWithRolesResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_user(current_user.id, data)
