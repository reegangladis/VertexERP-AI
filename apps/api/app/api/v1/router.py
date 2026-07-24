from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    version,
    auth,
    organization,
    user,
    role,
    permission,
    audit,
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["system"])
api_router.include_router(version.router, prefix="/version", tags=["system"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(organization.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(role.router, prefix="/roles", tags=["roles"])
api_router.include_router(permission.router, prefix="/permissions", tags=["permissions"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
