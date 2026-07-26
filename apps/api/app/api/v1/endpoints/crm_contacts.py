import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.crm_customer import Contact
from app.repositories.crm_mgmt import ContactRepository
from app.schemas.crm_mgmt import ContactResponse, ContactCreate
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

@router.get("", response_model=APIResponse[List[ContactResponse]])
async def list_contacts(
    customer_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    
    repo = ContactRepository(db)
    stmt = select(Contact).where(
        Contact.organization_id == current_user.organization_id,
        Contact.is_deleted == False
    )
    if customer_id:
        stmt = stmt.where(Contact.customer_id == customer_id)
        
    res = await db.execute(stmt)
    contacts = list(res.scalars().all())
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Contacts retrieved successfully",
        data=contacts
    )

@router.post("", response_model=APIResponse[ContactResponse])
async def create_contact(
    payload: ContactCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = ContactRepository(db)
    contact = await repo.create({
        "organization_id": current_user.organization_id,
        **payload.dict()
    })
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Contact created successfully",
        data=contact
    )
