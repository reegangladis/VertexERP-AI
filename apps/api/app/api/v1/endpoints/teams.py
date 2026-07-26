import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.team import Team
from app.repositories.org_mgmt import TeamRepository
from app.services.org_mgmt import TeamService, parse_csv_file, generate_csv_text, OrgMgmtServiceException
from app.schemas.org_mgmt import TeamResponse, TeamCreate, TeamUpdate, BulkDeleteRequest
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

async def get_team_service(db: AsyncSession = Depends(get_db_session)):
    return TeamService(TeamRepository(db))

@router.get("", response_model=APIResponse[List[TeamResponse]])
async def list_teams(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    department_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    service: TeamService = Depends(get_team_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    stmt = select(Team).where(
        Team.organization_id == current_user.organization_id,
        Team.is_deleted == False
    )
    if department_id:
        stmt = stmt.where(Team.department_id == department_id)
        
    if search:
        stmt = stmt.where(
            or_(
                Team.name.ilike(f"%{search}%"),
                Team.slug.ilike(f"%{search}%")
            )
        )
    
    if sort:
        descending = sort.startswith("-")
        field_name = sort.lstrip("-")
        if hasattr(Team, field_name):
            column = getattr(Team, field_name)
            stmt = stmt.order_by(column.desc() if descending else column.asc())
    else:
        stmt = stmt.order_by(Team.name.asc())

    stmt = stmt.offset(skip).limit(limit)
    res = await service.repository.db.execute(stmt)
    teams = list(res.scalars().all())

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Teams retrieved successfully",
        data=[TeamResponse.model_validate(t) for t in teams]
    )

@router.get("/{id}", response_model=APIResponse[TeamResponse])
async def get_team(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: TeamService = Depends(get_team_service)
):
    team = await service.get(id)
    if not team or team.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Team not found")
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Team details retrieved",
        data=TeamResponse.model_validate(team)
    )

@router.post("", response_model=APIResponse[TeamResponse])
async def create_team(
    payload: TeamCreate,
    current_user: User = Depends(get_current_user),
    service: TeamService = Depends(get_team_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    
    if payload.parent_team_id:
        parent = await service.get(payload.parent_team_id)
        if not parent or parent.organization_id != current_user.organization_id:
            raise HTTPException(status_code=400, detail="Invalid parent team")

    data = payload.model_dump()
    data["organization_id"] = current_user.organization_id
    
    team = await service.repository.create(data)
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Team created successfully",
        data=TeamResponse.model_validate(team)
    )

@router.put("/{id}", response_model=APIResponse[TeamResponse])
async def update_team(
    id: uuid.UUID,
    payload: TeamUpdate,
    current_user: User = Depends(get_current_user),
    service: TeamService = Depends(get_team_service)
):
    team = await service.get(id)
    if not team or team.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Team not found")

    if payload.parent_team_id:
        try:
            await service.validate_parent(id, payload.parent_team_id)
        except OrgMgmtServiceException as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        parent = await service.get(payload.parent_team_id)
        if not parent or parent.organization_id != current_user.organization_id:
            raise HTTPException(status_code=400, detail="Invalid parent team")

    updated = await service.update(id, payload)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Team updated successfully",
        data=TeamResponse.model_validate(updated)
    )

@router.delete("/{id}", response_model=APIResponse[TeamResponse])
async def delete_team(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: TeamService = Depends(get_team_service)
):
    team = await service.get(id)
    if not team or team.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Team not found")

    deleted = await service.delete(id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Team deleted successfully",
        data=TeamResponse.model_validate(deleted)
    )

@router.post("/bulk-delete", response_model=APIResponse[List[uuid.UUID]])
async def bulk_delete_teams(
    payload: BulkDeleteRequest,
    current_user: User = Depends(get_current_user),
    service: TeamService = Depends(get_team_service)
):
    deleted_ids = []
    for item_id in payload.ids:
        team = await service.get(item_id)
        if team and team.organization_id == current_user.organization_id:
            await service.delete(item_id)
            deleted_ids.append(item_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Bulk deletion completed",
        data=deleted_ids
    )

@router.post("/bulk-upload", response_model=APIResponse[List[TeamResponse]])
async def bulk_upload_teams(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: TeamService = Depends(get_team_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    
    content = await file.read()
    rows = parse_csv_file(content)
    
    created_teams = []
    for row in rows:
        name = row.get("name")
        slug = row.get("slug") or name.lower().replace(" ", "-") if name else None
        dept_id_str = row.get("department_id")
        if not name or not dept_id_str:
            continue
        try:
            dept_id = uuid.UUID(dept_id_str)
        except ValueError:
            continue
        
        team = await service.repository.create({
            "organization_id": current_user.organization_id,
            "department_id": dept_id,
            "name": name,
            "slug": slug,
            "description": row.get("description"),
            "status": row.get("status", "active")
        })
        created_teams.append(TeamResponse.model_validate(team))

    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message=f"Uploaded {len(created_teams)} teams successfully",
        data=created_teams
    )

@router.get("/export/csv")
async def export_teams_csv(
    current_user: User = Depends(get_current_user),
    service: TeamService = Depends(get_team_service)
):
    teams = await service.get_by_org(current_user.organization_id)
    headers = ["id", "department_id", "name", "slug", "description", "status"]
    rows = []
    for t in teams:
        rows.append({
            "id": str(t.id),
            "department_id": str(t.department_id),
            "name": t.name,
            "slug": t.slug,
            "description": t.description or "",
            "status": t.status
        })
    csv_text = generate_csv_text(headers, rows)
    
    from fastapi.responses import Response
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=teams.csv"}
    )
