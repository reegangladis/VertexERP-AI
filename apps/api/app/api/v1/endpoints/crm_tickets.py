import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_current_user, get_db_session
from app.models.crm_ticket import SupportTicket
from app.models.user import User
from app.repositories.crm_mgmt import SupportTicketRepository
from app.schemas.crm_mgmt import (
    SupportTicketCreate,
    SupportTicketResponse,
    SupportTicketUpdate,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()


@router.get("", response_model=APIResponse[list[SupportTicketResponse]])
async def list_tickets(
    customer_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    stmt = select(SupportTicket).where(
        SupportTicket.organization_id == current_user.organization_id,
        SupportTicket.is_deleted == False,
    )
    if customer_id:
        stmt = stmt.where(SupportTicket.customer_id == customer_id)

    res = await db.execute(stmt)
    tickets = list(res.scalars().all())
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Support tickets retrieved successfully",
        data=tickets,
    )


@router.post("", response_model=APIResponse[SupportTicketResponse])
async def create_ticket(
    payload: SupportTicketCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = SupportTicketRepository(db)
    ticket = await repo.create(
        {"organization_id": current_user.organization_id, **payload.dict()}
    )
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Support ticket registered successfully",
        data=ticket,
    )


@router.put("/{id}", response_model=APIResponse[SupportTicketResponse])
async def update_ticket(
    id: uuid.UUID,
    payload: SupportTicketUpdate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session),
):
    repo = SupportTicketRepository(db)
    ticket = await repo.get(id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")
    updated = await repo.update(ticket, payload.dict(exclude_unset=True))
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Support ticket updated",
        data=updated,
    )
