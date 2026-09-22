"""Employee Profile and supporting details schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --------------------------------------------------------------------------
# Profile
# --------------------------------------------------------------------------
class EmployeeProfileBase(BaseModel):
    marital_status: str | None = Field(None, max_length=32)
    blood_group: str | None = Field(None, max_length=16)
    nationality: str | None = Field(None, max_length=64)
    national_id_number: str | None = Field(None, max_length=64)
    passport_number: str | None = Field(None, max_length=64)
    tax_identification_number: str | None = Field(None, max_length=64)
    bio: str | None = None


class EmployeeProfileCreate(EmployeeProfileBase):
    pass


class EmployeeProfileUpdate(EmployeeProfileBase):
    pass


class EmployeeProfileResponse(EmployeeProfileBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Emergency Contact
# --------------------------------------------------------------------------
class EmergencyContactCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    relationship: str = Field(..., min_length=1, max_length=64)
    phone_number: str = Field(..., min_length=1, max_length=32)
    email: EmailStr | None = None
    is_primary: bool = False


class EmergencyContactResponse(EmergencyContactCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Address
# --------------------------------------------------------------------------
class AddressCreate(BaseModel):
    address_type: str = Field("RESIDENTIAL", max_length=32)
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: str | None = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=128)
    state: str = Field(..., min_length=1, max_length=128)
    postal_code: str = Field(..., min_length=1, max_length=32)
    country: str = Field("USA", max_length=64)
    is_primary: bool = False


class AddressResponse(AddressCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Bank Account (Sensitive Data)
# --------------------------------------------------------------------------
class BankAccountCreate(BaseModel):
    bank_name: str = Field(..., min_length=1, max_length=128)
    account_number: str = Field(..., min_length=4, max_length=64)
    routing_or_ifsc_code: str = Field(..., min_length=1, max_length=64)
    account_type: str = Field("CHECKING", max_length=32)
    is_primary: bool = True


class BankAccountResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    bank_name: str
    account_number_masked: str
    routing_or_ifsc_code: str
    account_type: str
    is_primary: bool
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Document Attachment
# --------------------------------------------------------------------------
class DocumentCreate(BaseModel):
    document_type: str = Field("OTHER", max_length=64)
    title: str = Field(..., min_length=1, max_length=255)
    file_url: str = Field(..., min_length=1, max_length=512)
    s3_key: str | None = Field(None, max_length=512)
    file_size_bytes: int = Field(0, ge=0)
    mime_type: str | None = Field(None, max_length=128)
    expiry_date: date | None = None
    is_verified: bool = False


class DocumentResponse(DocumentCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
