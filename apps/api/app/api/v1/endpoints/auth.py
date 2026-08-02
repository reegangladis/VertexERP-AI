"""
Auth API Endpoints — Enterprise Authentication & Identity Management.

Implements all authentication flows: registration, login, logout, token refresh,
forgot/reset password, email verification, profile management, session management,
login history, and audit logs.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user, get_db_session
from app.models.user import User
from app.schemas.auth import (
    AuditLogResponse,
    ChangePasswordInput,
    EmailVerificationInput,
    ForgotPasswordInput,
    ForgotPasswordResponse,
    LoginHistoryResponse,
    OrganizationRegister,
    RefreshInput,
    ResetPasswordInput,
    SessionResponse,
    TokenResponse,
    UserResponse,
    UserUpdate,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

logger = logging.getLogger(__name__)
router = APIRouter()


# ──────────────────────────────────────────
# Dependency: AuthService factory
# ──────────────────────────────────────────


async def get_auth_service(db: AsyncSession = Depends(get_db_session)):
    """Build and return a fully-wired AuthService instance."""
    from app.repositories.audit import AuditLogRepository, LoginHistoryRepository
    from app.repositories.organization import (
        OrganizationRepository,
        SecuritySettingRepository,
        TenantSettingRepository,
    )
    from app.repositories.role import RoleRepository
    from app.repositories.session import (
        RefreshTokenRepository,
        SessionRepository,
        TrustedDeviceRepository,
    )
    from app.repositories.token import (
        EmailVerificationTokenRepository,
        PasswordResetTokenRepository,
    )
    from app.repositories.user import PasswordHistoryRepository, UserRepository
    from app.services.audit import AuditService, LoginHistoryService
    from app.services.auth import AuthService
    from app.services.organization import OrganizationService
    from app.services.session import SessionService
    from app.services.user import UserService

    user_service = UserService(UserRepository(db), PasswordHistoryRepository(db))
    org_service = OrganizationService(
        OrganizationRepository(db),
        TenantSettingRepository(db),
        SecuritySettingRepository(db),
    )
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
        security_setting_repo=SecuritySettingRepository(db),
        password_reset_token_repo=PasswordResetTokenRepository(db),
        email_verification_token_repo=EmailVerificationTokenRepository(db),
    )


# ──────────────────────────────────────────
# Registration
# ──────────────────────────────────────────


@router.post(
    "/register",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Organization & Admin User",
    tags=["auth"],
)
async def register(
    payload: OrganizationRegister,
    request: Request,
    auth_service=Depends(get_auth_service),
):
    """
    Register a new organization and its first administrator account.
    Issues an email verification token (returned in dev mode via response).
    """
    ip = request.client.host if request.client else "127.0.0.1"
    ua = request.headers.get("user-agent", "N/A")

    user_data = {
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "email": payload.email,
        "phone": payload.phone,
        "password": payload.password,
    }

    user, verification_token = await auth_service.register(
        user_data=user_data,
        org_name=payload.org_name,
        org_slug=payload.org_slug,
        ip_address=ip,
        user_agent=ua,
        industry=payload.industry,
        company_size=payload.company_size,
        country=payload.country,
        timezone=payload.timezone,
    )

    response_data = {
        "user": UserResponse.model_validate(user).model_dump(),
        "message": "Organization created successfully. Please verify your email to activate your account.",
    }

    # Dev mode: include verification token in response for immediate testing
    if settings.ENVIRONMENT in ("development", "testing") and verification_token:
        response_data["verification_token"] = verification_token
        response_data["verification_link"] = (
            f"http://localhost:5173/auth/verify-email?token={verification_token}"
        )

    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Organization registered successfully",
        data=response_data,
    )


# ──────────────────────────────────────────
# Login
# ──────────────────────────────────────────


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    summary="User Login",
    tags=["auth"],
)
async def login(
    payload: dict,
    request: Request,
    auth_service=Depends(get_auth_service),
):
    """
    Authenticate with email + password.
    Returns JWT access token, refresh token, and session ID.
    """
    ip = request.client.host if request.client else "127.0.0.1"
    ua = request.headers.get("user-agent", "N/A")

    identifier = (
        payload.get("email")
        or payload.get("username")
        or payload.get("identifier")
        or ""
    )
    password = payload.get("password", "")

    if not identifier or not password:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email/username and password are required",
        )

    token_data = await auth_service.login(identifier, password, ip, ua)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Login successful",
        data=TokenResponse(**token_data),
    )


# ──────────────────────────────────────────
# Logout
# ──────────────────────────────────────────


@router.post(
    "/logout",
    summary="Logout Current Session",
    tags=["auth"],
)
async def logout(
    payload: RefreshInput,
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service=Depends(get_auth_service),
):
    """Revoke the current refresh token and terminate the active session."""
    ip = request.client.host if request.client else "127.0.0.1"
    ua = request.headers.get("user-agent", "N/A")

    await auth_service.logout(payload.refresh_token, current_user.id, ip, ua)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Logged out successfully",
    )


@router.delete(
    "/logout-all",
    summary="Logout All Sessions",
    tags=["auth"],
)
async def logout_all(
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service=Depends(get_auth_service),
):
    """Terminate ALL active sessions and revoke ALL refresh tokens for this account."""
    ip = request.client.host if request.client else "127.0.0.1"
    ua = request.headers.get("user-agent", "N/A")

    await auth_service.logout_all(current_user.id, ip, ua)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="All sessions terminated successfully",
    )


# ──────────────────────────────────────────
# Token Refresh
# ──────────────────────────────────────────


@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    summary="Refresh Access Token",
    tags=["auth"],
)
async def refresh(
    payload: RefreshInput,
    request: Request,
    auth_service=Depends(get_auth_service),
):
    """Exchange a valid refresh token for a new access + refresh token pair (rotation)."""
    ip = request.client.host if request.client else "127.0.0.1"
    ua = request.headers.get("user-agent", "N/A")

    token_data = await auth_service.refresh_tokens(payload.refresh_token, ip, ua)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Token refreshed successfully",
        data=TokenResponse(**token_data),
    )


# ──────────────────────────────────────────
# Current User
# ──────────────────────────────────────────


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Get Current User",
    tags=["auth"],
)
async def me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user profile."""
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="User profile retrieved successfully",
        data=UserResponse.model_validate(current_user),
    )


@router.put(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Update User Profile",
    tags=["auth"],
)
async def update_profile(
    payload: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service=Depends(get_auth_service),
):
    """Update the current user's profile fields (name, phone, avatar, timezone, language)."""
    update_data = payload.model_dump(exclude_unset=True)
    updated_user = await auth_service.update_profile(current_user, update_data)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Profile updated successfully",
        data=UserResponse.model_validate(updated_user),
    )


# ──────────────────────────────────────────
# Change Password
# ──────────────────────────────────────────


@router.put(
    "/change-password",
    summary="Change Password",
    tags=["auth"],
)
async def change_password(
    payload: ChangePasswordInput,
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service=Depends(get_auth_service),
):
    """Authenticated password change requiring the current password for verification."""
    ip = request.client.host if request.client else "127.0.0.1"
    ua = request.headers.get("user-agent", "N/A")

    await auth_service.change_password(
        user=current_user,
        old_password=payload.old_password,
        new_password=payload.new_password,
        confirm_password=payload.confirm_password,
        ip_address=ip,
        user_agent=ua,
    )
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Password changed successfully",
    )


# ──────────────────────────────────────────
# Forgot & Reset Password
# ──────────────────────────────────────────


@router.post(
    "/forgot-password",
    summary="Forgot Password — Initiate Recovery",
    tags=["auth"],
)
async def forgot_password(
    payload: ForgotPasswordInput,
    auth_service=Depends(get_auth_service),
):
    """
    Request a password reset token for the given email.
    In development mode, returns the token directly for testing.
    In production, sends it via email (email provider integration required).
    """
    token = await auth_service.forgot_password(payload.email)

    response_data = ForgotPasswordResponse(
        message="If this email is registered, password recovery instructions will be delivered shortly."
    )
    if token and settings.ENVIRONMENT in ("development", "testing"):
        response_data.reset_token = token

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message=response_data.message,
        data=response_data,
    )


@router.post(
    "/reset-password",
    summary="Reset Password with Token",
    tags=["auth"],
)
async def reset_password(
    payload: ResetPasswordInput,
    auth_service=Depends(get_auth_service),
):
    """Reset the user's password using a valid reset token from the recovery email."""
    await auth_service.reset_password(payload.token, payload.new_password)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Password reset successfully. You can now log in with your new password.",
    )


# ──────────────────────────────────────────
# Email Verification
# ──────────────────────────────────────────


@router.post(
    "/verify-email",
    summary="Verify Email Address",
    tags=["auth"],
)
async def verify_email(
    payload: EmailVerificationInput,
    auth_service=Depends(get_auth_service),
):
    """Activate user account by verifying the email address via token."""
    await auth_service.verify_email(payload.token)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Email verified successfully. Your account is now active.",
    )


@router.post(
    "/resend-verification",
    summary="Resend Email Verification",
    tags=["auth"],
)
async def resend_verification(
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service=Depends(get_auth_service),
):
    """Resend the email verification link for the authenticated user."""
    token = await auth_service.resend_verification_email(current_user.id)

    response_data: dict = {"message": "Verification email dispatched successfully."}
    if token and settings.ENVIRONMENT in ("development", "testing"):
        response_data["verification_token"] = token
        response_data["verification_link"] = (
            f"http://localhost:5173/auth/verify-email?token={token}"
        )

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Verification email sent",
        data=response_data,
    )


# ──────────────────────────────────────────
# Session Management
# ──────────────────────────────────────────


@router.get(
    "/sessions",
    response_model=APIResponse[list[SessionResponse]],
    summary="List Active Sessions",
    tags=["auth"],
)
async def get_sessions(
    current_user: User = Depends(get_current_user),
    auth_service=Depends(get_auth_service),
):
    """Return all active login sessions for the currently authenticated user."""
    sessions = await auth_service.get_sessions(current_user.id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Active sessions retrieved successfully",
        data=[SessionResponse.model_validate(s) for s in sessions],
    )


@router.delete(
    "/sessions/{session_id}",
    summary="Terminate a Session",
    tags=["auth"],
)
async def revoke_session(
    session_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service=Depends(get_auth_service),
):
    """Terminate a specific session by ID. The session must belong to the current user."""
    ip = request.client.host if request.client else "127.0.0.1"
    ua = request.headers.get("user-agent", "N/A")

    await auth_service.revoke_session(session_id, current_user.id, ip, ua)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Session terminated successfully",
    )


# ──────────────────────────────────────────
# Login History
# ──────────────────────────────────────────


@router.get(
    "/login-history",
    response_model=APIResponse[list[LoginHistoryResponse]],
    summary="Get Login History",
    tags=["auth"],
)
async def get_login_history(
    current_user: User = Depends(get_current_user),
    auth_service=Depends(get_auth_service),
):
    """Return the recent login history for the current user including success/failure events."""
    history = await auth_service.get_login_history(current_user.id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Login history retrieved successfully",
        data=[LoginHistoryResponse.model_validate(h) for h in history],
    )


# ──────────────────────────────────────────
# Audit Logs
# ──────────────────────────────────────────


@router.get(
    "/audit-logs",
    response_model=APIResponse[list[AuditLogResponse]],
    summary="Get Audit Logs",
    tags=["auth"],
)
async def get_audit_logs(
    current_user: User = Depends(get_current_user),
    auth_service=Depends(get_auth_service),
):
    """Return organization-level audit logs for the current user's organization."""
    if not current_user.organization_id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with an organization",
        )

    logs = await auth_service.get_audit_logs(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Audit logs retrieved successfully",
        data=[AuditLogResponse.model_validate(log) for log in logs],
    )
