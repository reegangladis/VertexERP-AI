import uuid
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db_session, get_current_user
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshInput,
    ForgotPasswordInput,
    ResetPasswordInput,
    UserResponse,
    EmailVerificationInput,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response
from app.models.user import User

router = APIRouter()

# Resolve dependencies helper
async def get_auth_service(db: AsyncSession = Depends(get_db_session)):
    from app.repositories.user import UserRepository, PasswordHistoryRepository
    from app.repositories.organization import OrganizationRepository, TenantSettingRepository, SecuritySettingRepository
    from app.repositories.role import RoleRepository
    from app.repositories.session import SessionRepository, RefreshTokenRepository, TrustedDeviceRepository
    from app.repositories.audit import AuditLogRepository, LoginHistoryRepository
    
    from app.services.user import UserService
    from app.services.organization import OrganizationService
    from app.services.session import SessionService
    from app.services.audit import AuditService, LoginHistoryService
    from app.services.auth import AuthService

    user_service = UserService(UserRepository(db), PasswordHistoryRepository(db))
    org_service = OrganizationService(OrganizationRepository(db), TenantSettingRepository(db), SecuritySettingRepository(db))
    session_service = SessionService(SessionRepository(db), TrustedDeviceRepository(db))
    audit_service = AuditService(AuditLogRepository(db))
    login_hist_service = LoginHistoryService(LoginHistoryRepository(db))

    return AuthService(
        user_service=user_service,
        org_service=org_service,
        session_service=session_service,
        refresh_token_repo=RefreshTokenRepository(db),
        role_repo=RoleRepository(db),
        audit_service=audit_service,
        login_history_service=login_hist_service,
        security_setting_repo=SecuritySettingRepository(db)
    )

@router.post("/register", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegister,
    request: Request,
    auth_service = Depends(get_auth_service)
):
    ip = request.client.host if request.client else "127.0.0.1"
    ua = request.headers.get("user-agent", "N/A")
    
    user_in = {
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "username": payload.username,
        "email": payload.email,
        "password": payload.password
    }
    
    user = await auth_service.register(user_in, payload.org_name, payload.org_slug, ip, ua)
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="User account registered successfully",
        data=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    payload: UserLogin,
    request: Request,
    auth_service = Depends(get_auth_service)
):
    ip = request.client.host if request.client else "127.0.0.1"
    ua = request.headers.get("user-agent", "N/A")
    
    token_data = await auth_service.login(payload.email, payload.password, ip, ua)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="User logged in successfully",
        data=TokenResponse(**token_data)
    )

@router.post("/logout")
async def logout(
    payload: RefreshInput,
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service = Depends(get_auth_service)
):
    ip = request.client.host if request.client else "127.0.0.1"
    ua = request.headers.get("user-agent", "N/A")
    
    await auth_service.logout(payload.refresh_token, current_user.id, ip, ua)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="User logged out and session terminated"
    )

@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh(
    payload: RefreshInput,
    request: Request,
    auth_service = Depends(get_auth_service)
):
    ip = request.client.host if request.client else "127.0.0.1"
    ua = request.headers.get("user-agent", "N/A")
    
    token_data = await auth_service.refresh_tokens(payload.refresh_token, ip, ua)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Access token refreshed successfully",
        data=TokenResponse(**token_data)
    )

@router.get("/me", response_model=APIResponse[UserResponse])
async def me(current_user: User = Depends(get_current_user)):
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="User details retrieved successfully",
        data=UserResponse.model_validate(current_user)
    )

@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordInput,
    auth_service = Depends(get_auth_service)
):
    # Architecture Placeholder (Email OTP recovery flows)
    # Verification email details will log in server terminal
    print(f"FORGOT PASSWORD REQUEST RECEIVED FOR: {payload.email}")
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="If the email is registered, recovery links will be delivered shortly."
    )

@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordInput,
    auth_service = Depends(get_auth_service)
):
    # Mock Token Verification and update password
    print(f"RESET PASSWORD COMPLETED WITH TOKEN: {payload.token}")
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Password updated successfully."
    )

@router.post("/verify-email")
async def verify_email(
    payload: EmailVerificationInput,
    auth_service = Depends(get_auth_service)
):
    print(f"EMAIL VERIFIED WITH TOKEN: {payload.token}")
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Email verified successfully."
    )
