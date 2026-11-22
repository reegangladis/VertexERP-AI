"""Aggregated Identity router mounting auth, mfa, user, and role sub-routers."""

from fastapi import APIRouter

from app.modules.identity.api.v1.auth_endpoints import router as auth_router
from app.modules.identity.api.v1.mfa_endpoints import router as mfa_router
from app.modules.identity.api.v1.role_endpoints import router as role_router
from app.modules.identity.api.v1.user_endpoints import router as user_router

router = APIRouter(prefix="/identity", tags=["Identity & Access Management"])

router.include_router(auth_router)
router.include_router(mfa_router)
router.include_router(user_router)
router.include_router(role_router)
