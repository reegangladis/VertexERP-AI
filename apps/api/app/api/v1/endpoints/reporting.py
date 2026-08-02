import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_user, get_db_session
from app.models.user import User
from app.schemas.org_mgmt import EmployeeNode, ReportingTreeNode
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()


def build_tree(users: list[User]) -> list[ReportingTreeNode]:
    # Create employee node map
    user_map = {}
    nodes_by_id = {}

    for u in users:
        desig_title = u.designation.title if u.designation else None
        job_lvl = u.designation.job_level if u.designation else None
        rep_lvl = u.designation.reporting_level if u.designation else None

        emp_node = EmployeeNode(
            id=u.id,
            first_name=u.first_name,
            last_name=u.last_name,
            email=u.email,
            designation_title=desig_title,
            job_level=job_lvl,
            reporting_level=rep_lvl,
        )
        tree_node = ReportingTreeNode(user=emp_node, subordinates=[])
        user_map[u.id] = u
        nodes_by_id[u.id] = tree_node

    roots = []
    for u in users:
        node = nodes_by_id[u.id]
        if u.manager_id and u.manager_id in nodes_by_id:
            parent_node = nodes_by_id[u.manager_id]
            parent_node.subordinates.append(node)
        else:
            roots.append(node)

    return roots


@router.get("/tree", response_model=APIResponse[list[ReportingTreeNode]])
async def get_reporting_tree(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    # Fetch all users with their designations loaded
    stmt = (
        select(User)
        .where(
            User.organization_id == current_user.organization_id,
            User.is_deleted == False,
        )
        .options(selectinload(User.designation))
    )
    result = await db.execute(stmt)
    users = list(result.scalars().all())

    tree = build_tree(users)

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Reporting structure tree retrieved successfully",
        data=tree,
    )


@router.put("/assign-manager", response_model=APIResponse[dict[str, Any]])
async def assign_manager(
    user_id: uuid.UUID,
    manager_id: uuid.UUID | None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    # Fetch user
    stmt = select(User).where(
        User.id == user_id, User.organization_id == current_user.organization_id
    )
    res = await db.execute(stmt)
    user_obj = res.scalar_one_or_none()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found in organization")

    if manager_id:
        if user_id == manager_id:
            raise HTTPException(
                status_code=400, detail="User cannot report to themselves"
            )

        stmt = select(User).where(
            User.id == manager_id, User.organization_id == current_user.organization_id
        )
        res = await db.execute(stmt)
        mgr_obj = res.scalar_one_or_none()
        if not mgr_obj:
            raise HTTPException(
                status_code=404, detail="Manager not found in organization"
            )

    user_obj.manager_id = manager_id
    db.add(user_obj)
    await db.commit()

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Manager assigned successfully",
        data={
            "user_id": str(user_id),
            "manager_id": str(manager_id) if manager_id else None,
        },
    )
