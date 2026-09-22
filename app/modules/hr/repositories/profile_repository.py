"""Profile and supporting entities repository."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hr.models.profile import (
    EmployeeAddress,
    EmployeeBankAccount,
    EmployeeDocument,
    EmployeeEmergencyContact,
    EmployeeProfile,
)


class ProfileRepository:
    """Repository for Profile details with strict tenant and org isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Profile
    async def get_profile(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> EmployeeProfile | None:
        stmt = select(EmployeeProfile).where(
            EmployeeProfile.employee_id == employee_id,
            EmployeeProfile.tenant_id == tenant_id,
            EmployeeProfile.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def save_profile(self, profile: EmployeeProfile) -> EmployeeProfile:
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def update_profile(self, profile: EmployeeProfile) -> EmployeeProfile:
        profile.updated_at = datetime.now(UTC)
        profile.version += 1
        await self.session.flush()
        return profile

    # Emergency Contacts
    async def list_emergency_contacts(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmployeeEmergencyContact]:
        stmt = (
            select(EmployeeEmergencyContact)
            .where(
                EmployeeEmergencyContact.employee_id == employee_id,
                EmployeeEmergencyContact.tenant_id == tenant_id,
                EmployeeEmergencyContact.organization_id == org_id,
            )
            .order_by(
                EmployeeEmergencyContact.is_primary.desc(), EmployeeEmergencyContact.name.asc()
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_emergency_contact(
        self, contact: EmployeeEmergencyContact
    ) -> EmployeeEmergencyContact:
        self.session.add(contact)
        await self.session.flush()
        return contact

    async def delete_emergency_contact(
        self, contact_id: uuid.UUID, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> bool:
        stmt = select(EmployeeEmergencyContact).where(
            EmployeeEmergencyContact.id == contact_id,
            EmployeeEmergencyContact.employee_id == employee_id,
            EmployeeEmergencyContact.tenant_id == tenant_id,
            EmployeeEmergencyContact.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        contact = result.scalar_one_or_none()
        if contact:
            await self.session.delete(contact)
            await self.session.flush()
            return True
        return False

    # Addresses
    async def list_addresses(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmployeeAddress]:
        stmt = (
            select(EmployeeAddress)
            .where(
                EmployeeAddress.employee_id == employee_id,
                EmployeeAddress.tenant_id == tenant_id,
                EmployeeAddress.organization_id == org_id,
            )
            .order_by(EmployeeAddress.is_primary.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_address(self, address: EmployeeAddress) -> EmployeeAddress:
        self.session.add(address)
        await self.session.flush()
        return address

    async def delete_address(
        self, address_id: uuid.UUID, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> bool:
        stmt = select(EmployeeAddress).where(
            EmployeeAddress.id == address_id,
            EmployeeAddress.employee_id == employee_id,
            EmployeeAddress.tenant_id == tenant_id,
            EmployeeAddress.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        addr = result.scalar_one_or_none()
        if addr:
            await self.session.delete(addr)
            await self.session.flush()
            return True
        return False

    # Bank Accounts
    async def list_bank_accounts(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmployeeBankAccount]:
        stmt = (
            select(EmployeeBankAccount)
            .where(
                EmployeeBankAccount.employee_id == employee_id,
                EmployeeBankAccount.tenant_id == tenant_id,
                EmployeeBankAccount.organization_id == org_id,
            )
            .order_by(EmployeeBankAccount.is_primary.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_bank_account(self, bank: EmployeeBankAccount) -> EmployeeBankAccount:
        self.session.add(bank)
        await self.session.flush()
        return bank

    # Documents
    async def list_documents(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[EmployeeDocument]:
        stmt = (
            select(EmployeeDocument)
            .where(
                EmployeeDocument.employee_id == employee_id,
                EmployeeDocument.tenant_id == tenant_id,
                EmployeeDocument.organization_id == org_id,
            )
            .order_by(EmployeeDocument.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_document(self, doc: EmployeeDocument) -> EmployeeDocument:
        self.session.add(doc)
        await self.session.flush()
        return doc
