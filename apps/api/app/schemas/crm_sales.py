import uuid
from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Lead Source & Lead Schemas ---
class LeadSourceBase(BaseModel):
    source_name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    is_active: bool = Field(default=True)


class LeadSourceCreate(LeadSourceBase):
    organization_id: uuid.UUID


class LeadSourceUpdate(BaseModel):
    source_name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    is_active: bool | None = None


class LeadSourceResponse(LeadSourceBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadActivityBase(BaseModel):
    activity_type: str = Field(..., max_length=50)
    description: str = Field(..., max_length=2000)


class LeadActivityCreate(LeadActivityBase):
    lead_id: uuid.UUID
    performed_by: uuid.UUID | None = None


class LeadActivityResponse(LeadActivityBase):
    id: uuid.UUID
    lead_id: uuid.UUID
    performed_by: uuid.UUID | None = None
    performed_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    contact_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str | None = Field(None, max_length=50)
    website: str | None = Field(None, max_length=255)
    industry: str | None = Field(None, max_length=100)
    status: str = Field(default="New", max_length=50)
    priority: str = Field(default="Medium", max_length=50)
    expected_value: float = Field(default=0.0, ge=0)
    remarks: str | None = Field(None, max_length=2000)


class LeadCreate(LeadBase):
    organization_id: uuid.UUID
    lead_source_id: uuid.UUID | None = None
    assigned_to: uuid.UUID | None = None


class LeadUpdate(BaseModel):
    company_name: str | None = Field(None, min_length=1, max_length=255)
    contact_name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    website: str | None = Field(None, max_length=255)
    industry: str | None = Field(None, max_length=100)
    status: str | None = Field(None, max_length=50)
    priority: str | None = Field(None, max_length=50)
    expected_value: float | None = Field(None, ge=0)
    remarks: str | None = Field(None, max_length=2000)
    assigned_to: uuid.UUID | None = None


class LeadConvertPayload(BaseModel):
    customer_code: str | None = Field(None, max_length=50)
    opportunity_title: str | None = Field(None, max_length=255)
    expected_revenue: float | None = Field(None, ge=0)


class LeadAssignPayload(BaseModel):
    assigned_to: uuid.UUID


class LeadResponse(LeadBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    lead_source_id: uuid.UUID | None = None
    assigned_to: uuid.UUID | None = None
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    activities: list[LeadActivityResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Customer & Sub-entity Schemas ---
class CustomerContactBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    designation: str | None = Field(None, max_length=100)
    email: EmailStr
    phone: str | None = Field(None, max_length=50)
    mobile: str | None = Field(None, max_length=50)
    is_primary: bool = Field(default=False)


class CustomerContactCreate(CustomerContactBase):
    customer_id: uuid.UUID


class CustomerContactUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    designation: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    mobile: str | None = Field(None, max_length=50)
    is_primary: bool | None = None


class CustomerContactResponse(CustomerContactBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerAddressBase(BaseModel):
    address_type: str = Field(default="Billing", max_length=50)
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: str | None = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str | None = Field(None, max_length=100)
    country: str = Field(default="United States", max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    is_primary: bool = Field(default=True)


class CustomerAddressCreate(CustomerAddressBase):
    customer_id: uuid.UUID


class CustomerAddressUpdate(BaseModel):
    address_type: str | None = Field(None, max_length=50)
    address_line1: str | None = Field(None, min_length=1, max_length=255)
    address_line2: str | None = Field(None, max_length=255)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    is_primary: bool | None = None


class CustomerAddressResponse(CustomerAddressBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerNoteCreate(BaseModel):
    customer_id: uuid.UUID
    note: str = Field(..., min_length=1, max_length=4000)
    created_by: uuid.UUID | None = None


class CustomerNoteResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    note: str
    created_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerDocumentCreate(BaseModel):
    customer_id: uuid.UUID
    document_name: str = Field(..., min_length=1, max_length=255)
    document_type: str = Field(default="Contract", max_length=100)
    file_url: str = Field(..., max_length=500)
    uploaded_by: uuid.UUID | None = None


class CustomerDocumentResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    document_name: str
    document_type: str
    file_url: str
    uploaded_by: uuid.UUID | None = None
    uploaded_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerBase(BaseModel):
    customer_code: str = Field(..., min_length=1, max_length=50)
    company_name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str | None = Field(None, max_length=50)
    website: str | None = Field(None, max_length=255)
    industry: str | None = Field(None, max_length=100)
    tax_number: str | None = Field(None, max_length=50)
    credit_limit: float = Field(default=0.0, ge=0)
    payment_terms: str = Field(default="Net 30", max_length=100)
    status: str = Field(default="Active", max_length=50)


class CustomerCreate(CustomerBase):
    organization_id: uuid.UUID


class CustomerUpdate(BaseModel):
    customer_code: str | None = Field(None, min_length=1, max_length=50)
    company_name: str | None = Field(None, min_length=1, max_length=255)
    display_name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    website: str | None = Field(None, max_length=255)
    industry: str | None = Field(None, max_length=100)
    tax_number: str | None = Field(None, max_length=50)
    credit_limit: float | None = Field(None, ge=0)
    payment_terms: str | None = Field(None, max_length=100)
    status: str | None = Field(None, max_length=50)


class CustomerResponse(CustomerBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    contacts: list[CustomerContactResponse] = Field(default_factory=list)
    addresses: list[CustomerAddressResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Opportunity Schemas ---
class OpportunityBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    expected_revenue: float = Field(default=0.0, ge=0)
    probability: float = Field(default=50.0, ge=0, le=100)
    stage: str = Field(default="Qualification", max_length=50)
    expected_close_date: date
    status: str = Field(default="Open", max_length=50)


class OpportunityCreate(OpportunityBase):
    customer_id: uuid.UUID
    assigned_to: uuid.UUID | None = None


class OpportunityUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    expected_revenue: float | None = Field(None, ge=0)
    probability: float | None = Field(None, ge=0, le=100)
    stage: str | None = Field(None, max_length=50)
    expected_close_date: date | None = None
    assigned_to: uuid.UUID | None = None
    status: str | None = Field(None, max_length=50)


class OpportunityResponse(OpportunityBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    assigned_to: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Quotation & Sales Order Schemas ---
class QuotationItemBase(BaseModel):
    item_name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    quantity: float = Field(default=1.0, gt=0)
    unit_price: float = Field(default=0.0, ge=0)
    tax_amount: float = Field(default=0.0, ge=0)


class QuotationItemCreate(QuotationItemBase):
    pass


class QuotationItemResponse(QuotationItemBase):
    id: uuid.UUID
    quotation_id: uuid.UUID
    subtotal: float
    total_price: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuotationBase(BaseModel):
    quotation_number: str = Field(..., min_length=1, max_length=100)
    quotation_date: date
    valid_until: date
    discount: float = Field(default=0.0, ge=0)
    status: str = Field(default="Draft", max_length=50)


class QuotationCreate(QuotationBase):
    customer_id: uuid.UUID
    items: list[QuotationItemCreate] = Field(..., min_length=1)


class QuotationUpdate(BaseModel):
    quotation_date: date | None = None
    valid_until: date | None = None
    discount: float | None = Field(None, ge=0)
    status: str | None = Field(None, max_length=50)


class QuotationResponse(QuotationBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    subtotal: float
    tax: float
    grand_total: float
    created_at: datetime
    updated_at: datetime
    items: list[QuotationItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SalesOrderItemBase(BaseModel):
    item_name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    quantity: float = Field(default=1.0, gt=0)
    unit_price: float = Field(default=0.0, ge=0)
    tax_amount: float = Field(default=0.0, ge=0)


class SalesOrderItemCreate(SalesOrderItemBase):
    pass


class SalesOrderItemResponse(SalesOrderItemBase):
    id: uuid.UUID
    sales_order_id: uuid.UUID
    subtotal: float
    total_price: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SalesOrderBase(BaseModel):
    sales_order_number: str = Field(..., min_length=1, max_length=100)
    order_date: date
    discount: float = Field(default=0.0, ge=0)
    status: str = Field(default="Pending", max_length=50)


class SalesOrderCreate(SalesOrderBase):
    customer_id: uuid.UUID
    quotation_id: uuid.UUID | None = None
    items: list[SalesOrderItemCreate] = Field(..., min_length=1)


class SalesOrderUpdate(BaseModel):
    order_date: date | None = None
    discount: float | None = Field(None, ge=0)
    status: str | None = Field(None, max_length=50)


class SalesOrderResponse(SalesOrderBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    quotation_id: uuid.UUID | None = None
    subtotal: float
    tax: float
    grand_total: float
    created_at: datetime
    updated_at: datetime
    items: list[SalesOrderItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Task, Meeting & Customer Timeline Schemas ---
class CRMTaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    priority: str = Field(default="Medium", max_length=50)
    due_date: date
    status: str = Field(default="Pending", max_length=50)


class CRMTaskCreate(CRMTaskBase):
    customer_id: uuid.UUID | None = None
    assigned_to: uuid.UUID | None = None


class CRMTaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    priority: str | None = Field(None, max_length=50)
    due_date: date | None = None
    status: str | None = Field(None, max_length=50)
    assigned_to: uuid.UUID | None = None


class CRMTaskResponse(CRMTaskBase):
    id: uuid.UUID
    customer_id: uuid.UUID | None = None
    assigned_to: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MeetingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    agenda: str | None = Field(None, max_length=2000)
    meeting_date: datetime
    location: str | None = Field(None, max_length=255)
    meeting_type: str = Field(default="Online", max_length=50)
    status: str = Field(default="Scheduled", max_length=50)


class MeetingCreate(MeetingBase):
    customer_id: uuid.UUID | None = None


class MeetingUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    agenda: str | None = Field(None, max_length=2000)
    meeting_date: datetime | None = None
    location: str | None = Field(None, max_length=255)
    meeting_type: str | None = Field(None, max_length=50)
    status: str | None = Field(None, max_length=50)


class MeetingResponse(MeetingBase):
    id: uuid.UUID
    customer_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerTimelineResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    event_type: str
    title: str
    description: str | None = None
    event_time: datetime
    performed_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Dashboard Summary Schema ---
class CRMDashboardSummary(BaseModel):
    total_leads: int
    qualified_leads: int
    total_customers: int
    open_opportunities: int
    pipeline_value: float
    sales_revenue: float
    pending_quotations: int
    total_sales_orders: int
    meetings_today: int
    tasks_due: int
