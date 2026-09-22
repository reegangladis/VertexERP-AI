"""Employee Profile, Emergency Contacts, Addresses, Bank, and Document API endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.audit.services.audit_service import AuditService
from app.modules.hr.schemas.profile import (
    AddressCreate,
    AddressResponse,
    BankAccountCreate,
    BankAccountResponse,
    DocumentCreate,
    DocumentResponse,
    EmergencyContactCreate,
    EmergencyContactResponse,
    EmployeeProfileResponse,
    EmployeeProfileUpdate,
)
from app.modules.hr.services.profile_service import ProfileService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.modules.identity.models.user import User

router = APIRouter(prefix="/employees/{employee_id}", tags=["HR Employee Profiles"])


# --------------------------------------------------------------------------
# Extended Profile
# --------------------------------------------------------------------------
@router.get(
    "/profile",
    response_model=EmployeeProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Employee Profile",
    dependencies=[Depends(require_permission(PermissionCode.HR_PROFILES_READ.value))],
)
async def get_profile(
    employee_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> EmployeeProfileResponse:
    """Retrieves personal & demographic profile."""
    service = ProfileService(db)
    profile = await service.get_or_create_profile(employee_id, tenant_id, org_id)
    return EmployeeProfileResponse.model_validate(profile)


@router.put(
    "/profile",
    response_model=EmployeeProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Employee Profile",
    dependencies=[Depends(require_permission(PermissionCode.HR_PROFILES_WRITE.value))],
)
async def update_profile(
    employee_id: uuid.UUID,
    req: EmployeeProfileUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmployeeProfileResponse:
    """Updates personal & demographic profile."""
    service = ProfileService(db)
    profile = await service.update_profile(employee_id, tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_PROFILE_UPDATED",
        description=f"Profile for employee '{employee_id}' updated by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return EmployeeProfileResponse.model_validate(profile)


# --------------------------------------------------------------------------
# Emergency Contacts
# --------------------------------------------------------------------------
@router.get(
    "/emergency-contacts",
    response_model=list[EmergencyContactResponse],
    status_code=status.HTTP_200_OK,
    summary="List Emergency Contacts",
    dependencies=[Depends(require_permission(PermissionCode.HR_PROFILES_READ.value))],
)
async def list_emergency_contacts(
    employee_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[EmergencyContactResponse]:
    """Lists emergency contacts."""
    service = ProfileService(db)
    contacts = await service.list_emergency_contacts(employee_id, tenant_id, org_id)
    return [EmergencyContactResponse.model_validate(c) for c in contacts]


@router.post(
    "/emergency-contacts",
    response_model=EmergencyContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Emergency Contact",
    dependencies=[Depends(require_permission(PermissionCode.HR_PROFILES_WRITE.value))],
)
async def add_emergency_contact(
    employee_id: uuid.UUID,
    req: EmergencyContactCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmergencyContactResponse:
    """Adds an emergency contact."""
    service = ProfileService(db)
    contact = await service.add_emergency_contact(employee_id, tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_EMERGENCY_CONTACT_ADDED",
        description=f"Emergency contact '{contact.name}' added for employee '{employee_id}' by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return EmergencyContactResponse.model_validate(contact)


@router.delete(
    "/emergency-contacts/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Emergency Contact",
    dependencies=[Depends(require_permission(PermissionCode.HR_PROFILES_WRITE.value))],
)
async def delete_emergency_contact(
    employee_id: uuid.UUID,
    contact_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Deletes an emergency contact."""
    service = ProfileService(db)
    await service.delete_emergency_contact(contact_id, employee_id, tenant_id, org_id)


# --------------------------------------------------------------------------
# Addresses
# --------------------------------------------------------------------------
@router.get(
    "/addresses",
    response_model=list[AddressResponse],
    status_code=status.HTTP_200_OK,
    summary="List Addresses",
    dependencies=[Depends(require_permission(PermissionCode.HR_PROFILES_READ.value))],
)
async def list_addresses(
    employee_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[AddressResponse]:
    """Lists employee addresses."""
    service = ProfileService(db)
    addresses = await service.list_addresses(employee_id, tenant_id, org_id)
    return [AddressResponse.model_validate(a) for a in addresses]


@router.post(
    "/addresses",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Address",
    dependencies=[Depends(require_permission(PermissionCode.HR_PROFILES_WRITE.value))],
)
async def add_address(
    employee_id: uuid.UUID,
    req: AddressCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AddressResponse:
    """Adds an address."""
    service = ProfileService(db)
    addr = await service.add_address(employee_id, tenant_id, org_id, req)
    return AddressResponse.model_validate(addr)


# --------------------------------------------------------------------------
# Bank Accounts (Sensitive Data - Requires HR_PROFILES_SENSITIVE_READ)
# --------------------------------------------------------------------------
@router.get(
    "/bank-accounts",
    response_model=list[BankAccountResponse],
    status_code=status.HTTP_200_OK,
    summary="List Bank Accounts (Sensitive)",
    dependencies=[Depends(require_permission(PermissionCode.HR_PROFILES_SENSITIVE_READ.value))],
)
async def list_bank_accounts(
    employee_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[BankAccountResponse]:
    """Lists masked bank accounts (Requires sensitive read permissions)."""
    service = ProfileService(db)
    banks = await service.list_bank_accounts(employee_id, tenant_id, org_id)
    return [BankAccountResponse.model_validate(b) for b in banks]


@router.post(
    "/bank-accounts",
    response_model=BankAccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Bank Account",
    dependencies=[Depends(require_permission(PermissionCode.HR_PROFILES_WRITE.value))],
)
async def add_bank_account(
    employee_id: uuid.UUID,
    req: BankAccountCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BankAccountResponse:
    """Adds a bank account for direct deposit."""
    service = ProfileService(db)
    bank = await service.add_bank_account(employee_id, tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_BANK_ACCOUNT_ADDED",
        description=f"Bank account ({bank.bank_name}, {bank.account_number_masked}) registered for employee '{employee_id}' by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return BankAccountResponse.model_validate(bank)


# --------------------------------------------------------------------------
# Employee Documents
# --------------------------------------------------------------------------
@router.get(
    "/documents",
    response_model=list[DocumentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Employee Documents",
    dependencies=[Depends(require_permission(PermissionCode.HR_PROFILES_READ.value))],
)
async def list_documents(
    employee_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[DocumentResponse]:
    """Lists digital compliance and HR files."""
    service = ProfileService(db)
    docs = await service.list_documents(employee_id, tenant_id, org_id)
    return [DocumentResponse.model_validate(d) for d in docs]


@router.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Attach Employee Document",
    dependencies=[Depends(require_permission(PermissionCode.HR_PROFILES_WRITE.value))],
)
async def add_document(
    employee_id: uuid.UUID,
    req: DocumentCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """Attaches a digital document record."""
    service = ProfileService(db)
    doc = await service.add_document(employee_id, tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_DOCUMENT_UPLOADED",
        description=f"Document '{doc.title}' ({doc.document_type}) uploaded for employee '{employee_id}' by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return DocumentResponse.model_validate(doc)
