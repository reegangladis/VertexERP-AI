from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_db_session
from app.models.user import User
from app.schemas.permission import PermissionResponse
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()


# Services
async def get_permission_service(db: AsyncSession = Depends(get_db_session)):
    from app.repositories.permission import PermissionRepository
    from app.services.permission import PermissionService

    return PermissionService(PermissionRepository(db))


@router.get("", response_model=APIResponse[list[PermissionResponse]])
async def list_permissions(
    current_user: User = Depends(PermissionChecker("roles.read")),
    perm_service=Depends(get_permission_service),
):
    # Ensure database is seeded with defaults
    await perm_service.seed_default_permissions()

    permissions = await perm_service.repository.get_all()
    data = [PermissionResponse.model_validate(p) for p in permissions]
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="System permissions retrieved successfully",
        data=data,
    )
