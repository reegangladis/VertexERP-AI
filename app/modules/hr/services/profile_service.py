"""Profile service."""

import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.hr.models.profile import (
    EmployeeAddress,
    EmployeeBankAccount,
    EmployeeDocument,
    EmployeeEmergencyContact,
    EmployeeProfile,
)
from app.modules.hr.repositories.employee_repository import EmployeeRepository
from app.modules.hr.repositories.profile_repository import ProfileRepository
from app.modules.hr.schemas.profile import (
    AddressCreate,
    BankAccountCreate,
    DocumentCreate,
    EmergencyContactCreate,
    EmployeeProfileUpdate,
)


class ProfileService:
    """Business service for Employee extended profiles and sensitive records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.profile_repo = ProfileRepository(session)
        self.employee_repo = EmployeeRepository(session)

    async def _ensure_employee_exists(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> None:
        emp = await self.employee_repo.get_by_id(employee_id, tenant_id, org_id)
        if not emp:
            raise NotFoundException(f"Employee '{employee_id}' not found")

    async def get_or_create_profile(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> EmployeeProfile:
        await self._ensure_employee_exists(employee_id, tenant_id, org_id)
        profile = await self.profile_repo.get_profile(employee_id, tenant_id, org_id)
        if not profile:
            profile = EmployeeProfile(
                tenant_id=tenant_id,
                organization_id=org_id,
                employee_id=employee_id,
            )
            profile = await self.profile_repo.save_profile(profile)
        return profile

    async def update_profile(
        self,
        employee_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: EmployeeProfileUpdate,
    ) -> EmployeeProfile:
        profile = await self.get_or_create_profile(employee_id, tenant_id, org_id)
        if data.marital_status is not None:
            profile.marital_status = data.marital_status
        if data.blood_group is not None:
            profile.blood_group = data.blood_group
        if data.nationality is not None:
            profile.nationality = data.nationality
        if data.national_id_number is not None:
            profile.national_id_number = data.national_id_number
        if data.passport_number is not None:
            profile.passport_number = data.passport_number
        if data.tax_identification_number is not None:
            profile.tax_identification_number = data.tax_identification_number
        if data.bio is not None:
            profile.bio = data.bio
        return await self.profile_repo.update_profile(profile)

    # Emergency Contacts
    async def list_emergency_contacts(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmployeeEmergencyContact]:
        await self._ensure_employee_exists(employee_id, tenant_id, org_id)
        return await self.profile_repo.list_emergency_contacts(employee_id, tenant_id, org_id)

    async def add_emergency_contact(
        self,
        employee_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: EmergencyContactCreate,
    ) -> EmployeeEmergencyContact:
        await self._ensure_employee_exists(employee_id, tenant_id, org_id)
        contact = EmployeeEmergencyContact(
            tenant_id=tenant_id,
            organization_id=org_id,
            employee_id=employee_id,
            name=data.name,
            relationship=data.relationship,
            phone_number=data.phone_number,
            email=data.email,
            is_primary=data.is_primary,
        )
        return await self.profile_repo.add_emergency_contact(contact)

    async def delete_emergency_contact(
        self, contact_id: uuid.UUID, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> None:
        deleted = await self.profile_repo.delete_emergency_contact(
            contact_id, employee_id, tenant_id, org_id
        )
        if not deleted:
            raise NotFoundException(f"Emergency contact '{contact_id}' not found")

    # Addresses
    async def list_addresses(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmployeeAddress]:
        await self._ensure_employee_exists(employee_id, tenant_id, org_id)
        return await self.profile_repo.list_addresses(employee_id, tenant_id, org_id)

    async def add_address(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, data: AddressCreate
    ) -> EmployeeAddress:
        await self._ensure_employee_exists(employee_id, tenant_id, org_id)
        addr = EmployeeAddress(
            tenant_id=tenant_id,
            organization_id=org_id,
            employee_id=employee_id,
            address_type=data.address_type,
            address_line1=data.address_line1,
            address_line2=data.address_line2,
            city=data.city,
            state=data.state,
            postal_code=data.postal_code,
            country=data.country,
            is_primary=data.is_primary,
        )
        return await self.profile_repo.add_address(addr)

    # Bank Accounts
    async def list_bank_accounts(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmployeeBankAccount]:
        await self._ensure_employee_exists(employee_id, tenant_id, org_id)
        return await self.profile_repo.list_bank_accounts(employee_id, tenant_id, org_id)

    async def add_bank_account(
        self,
        employee_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: BankAccountCreate,
    ) -> EmployeeBankAccount:
        await self._ensure_employee_exists(employee_id, tenant_id, org_id)
        # Mask account number: preserve last 4 digits
        raw = data.account_number.strip()
        masked = f"{'*' * (len(raw) - 4)}{raw[-4:]}" if len(raw) > 4 else "****"
        bank = EmployeeBankAccount(
            tenant_id=tenant_id,
            organization_id=org_id,
            employee_id=employee_id,
            bank_name=data.bank_name,
            account_number_masked=masked,
            routing_or_ifsc_code=data.routing_or_ifsc_code,
            account_type=data.account_type,
            is_primary=data.is_primary,
        )
        return await self.profile_repo.add_bank_account(bank)

    # Documents
    async def list_documents(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmployeeDocument]:
        await self._ensure_employee_exists(employee_id, tenant_id, org_id)
        return await self.profile_repo.list_documents(employee_id, tenant_id, org_id)

    async def add_document(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID, data: DocumentCreate
    ) -> EmployeeDocument:
        await self._ensure_employee_exists(employee_id, tenant_id, org_id)
        doc = EmployeeDocument(
            tenant_id=tenant_id,
            organization_id=org_id,
            employee_id=employee_id,
            document_type=data.document_type,
            title=data.title,
            file_url=data.file_url,
            s3_key=data.s3_key,
            file_size_bytes=data.file_size_bytes,
            mime_type=data.mime_type,
            expiry_date=data.expiry_date,
            is_verified=data.is_verified,
        )
        return await self.profile_repo.add_document(doc)
