import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db_session
from app.models.branch import Branch
from app.models.user import User
from app.repositories.org_mgmt import BranchRepository
from app.schemas.org_mgmt import (
    BranchCreate,
    BranchResponse,
    BranchUpdate,
    BulkDeleteRequest,
)
from app.schemas.response import APIResponse
from app.services.org_mgmt import (
    BranchService,
    OrgMgmtServiceException,
    generate_csv_text,
    parse_csv_file,
)
from app.utils.response import standard_json_response

router = APIRouter()


async def get_branch_service(db: AsyncSession = Depends(get_db_session)):
    return BranchService(BranchRepository(db))


@router.get("", response_model=APIResponse[list[BranchResponse]])
async def list_branches(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    sort: str | None = None,
    current_user: User = Depends(get_current_user),
    service: BranchService = Depends(get_branch_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    # Search and filtering
    stmt = select(Branch).where(
        Branch.organization_id == current_user.organization_id,
        Branch.is_deleted == False,
    )
    if search:
        stmt = stmt.where(
            or_(
                Branch.name.ilike(f"%{search}%"),
                Branch.slug.ilike(f"%{search}%"),
                Branch.code.ilike(f"%{search}%"),
            )
        )

    # Sorting
    if sort:
        descending = sort.startswith("-")
        field_name = sort.lstrip("-")
        if hasattr(Branch, field_name):
            column = getattr(Branch, field_name)
            stmt = stmt.order_by(column.desc() if descending else column.asc())
    else:
        stmt = stmt.order_by(Branch.name.asc())

    stmt = stmt.offset(skip).limit(limit)
    res = await service.repository.db.execute(stmt)
    branches = list(res.scalars().all())

    # Get total count for metadata if needed (simplified)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Branches retrieved successfully",
        data=[BranchResponse.model_validate(b) for b in branches],
    )


@router.get("/{id}", response_model=APIResponse[BranchResponse])
async def get_branch(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: BranchService = Depends(get_branch_service),
):
    branch = await service.get(id)
    if not branch or branch.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Branch not found")
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Branch details retrieved",
        data=BranchResponse.model_validate(branch),
    )


@router.post("", response_model=APIResponse[BranchResponse])
async def create_branch(
    payload: BranchCreate,
    current_user: User = Depends(get_current_user),
    service: BranchService = Depends(get_branch_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    # Check parent loop
    if payload.parent_branch_id:
        parent = await service.get(payload.parent_branch_id)
        if not parent or parent.organization_id != current_user.organization_id:
            raise HTTPException(status_code=400, detail="Invalid parent branch")

    data = payload.model_dump()
    data["organization_id"] = current_user.organization_id

    branch = await service.repository.create(data)
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Branch created successfully",
        data=BranchResponse.model_validate(branch),
    )


@router.put("/{id}", response_model=APIResponse[BranchResponse])
async def update_branch(
    id: uuid.UUID,
    payload: BranchUpdate,
    current_user: User = Depends(get_current_user),
    service: BranchService = Depends(get_branch_service),
):
    branch = await service.get(id)
    if not branch or branch.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Branch not found")

    if payload.parent_branch_id:
        # Validate parent loops
        try:
            await service.validate_parent(id, payload.parent_branch_id)
        except OrgMgmtServiceException as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        parent = await service.get(payload.parent_branch_id)
        if not parent or parent.organization_id != current_user.organization_id:
            raise HTTPException(status_code=400, detail="Invalid parent branch")

    updated = await service.update(id, payload)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Branch updated successfully",
        data=BranchResponse.model_validate(updated),
    )


@router.delete("/{id}", response_model=APIResponse[BranchResponse])
async def delete_branch(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: BranchService = Depends(get_branch_service),
):
    branch = await service.get(id)
    if not branch or branch.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Branch not found")

    deleted = await service.delete(id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Branch deleted successfully",
        data=BranchResponse.model_validate(deleted),
    )


@router.post("/bulk-delete", response_model=APIResponse[list[uuid.UUID]])
async def bulk_delete_branches(
    payload: BulkDeleteRequest,
    current_user: User = Depends(get_current_user),
    service: BranchService = Depends(get_branch_service),
):
    deleted_ids = []
    for item_id in payload.ids:
        branch = await service.get(item_id)
        if branch and branch.organization_id == current_user.organization_id:
            await service.delete(item_id)
            deleted_ids.append(item_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Bulk deletion completed",
        data=deleted_ids,
    )


@router.post("/bulk-upload", response_model=APIResponse[list[BranchResponse]])
async def bulk_upload_branches(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: BranchService = Depends(get_branch_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    content = await file.read()
    rows = parse_csv_file(content)

    created_branches = []
    for row in rows:
        name = row.get("name")
        slug = row.get("slug") or name.lower().replace(" ", "-") if name else None
        if not name:
            continue

        branch = await service.repository.create(
            {
                "organization_id": current_user.organization_id,
                "name": name,
                "slug": slug,
                "code": row.get("code"),
                "timezone": row.get("timezone", "UTC"),
                "address_line1": row.get("address_line1"),
                "country": row.get("country"),
                "city": row.get("city"),
            }
        )
        created_branches.append(BranchResponse.model_validate(branch))

    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message=f"Uploaded {len(created_branches)} branches successfully",
        data=created_branches,
    )


@router.get("/export/csv")
async def export_branches_csv(
    current_user: User = Depends(get_current_user),
    service: BranchService = Depends(get_branch_service),
):
    branches = await service.get_by_org(current_user.organization_id)
    headers = ["id", "name", "slug", "code", "timezone", "country", "city"]
    rows = []
    for b in branches:
        rows.append(
            {
                "id": str(b.id),
                "name": b.name,
                "slug": b.slug,
                "code": b.code or "",
                "timezone": b.timezone,
                "country": b.country or "",
                "city": b.city or "",
            }
        )
    csv_text = generate_csv_text(headers, rows)

    # Return as simple download
    from fastapi.responses import Response

    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=branches.csv"},
    )
