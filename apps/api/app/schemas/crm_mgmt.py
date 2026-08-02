import uuid
from datetime import date, datetime

from pydantic import BaseModel


class CRMBaseModel(BaseModel):
    class Config:
        from_attributes = True


# 1. Lead & Source Schemas
class LeadSourceCreate(CRMBaseModel):
    name: str
    code: str


class LeadSourceResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str


class LeadCreate(CRMBaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    company: str | None = None
    status: str = "new"
    lead_source_id: uuid.UUID | None = None
    assigned_to_id: uuid.UUID | None = None


class LeadUpdate(CRMBaseModel):
    first_name: str | None = None
    last_name: str | None = None
    status: str | None = None
    assigned_to_id: uuid.UUID | None = None


class LeadResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    company: str | None = None
    status: str
    lead_source_id: uuid.UUID | None = None
    score: int
    assigned_to_id: uuid.UUID | None = None


class LeadConvertRequest(CRMBaseModel):
    customer_name: str | None = None
    create_opportunity: bool = True
    opportunity_title: str | None = None
    deal_amount: float | None = 0.0


# 2. Customer & Contact Schemas
class ContactCreate(CRMBaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    job_title: str | None = None
    department: str | None = None
    is_primary: bool = False


class ContactResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    customer_id: uuid.UUID | None = None
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    job_title: str | None = None
    department: str | None = None
    is_primary: bool


class CustomerCreate(CRMBaseModel):
    type: str = "business"
    name: str
    industry: str | None = None
    status: str = "active"
    communication_preferences: dict | None = None
    tags: list[str] | None = None
    contacts: list[ContactCreate] | None = None


class CustomerUpdate(CRMBaseModel):
    name: str | None = None
    industry: str | None = None
    status: str | None = None
    tags: list[str] | None = None


class CustomerResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    type: str
    name: str
    industry: str | None = None
    status: str
    communication_preferences: dict | None = None
    tags: dict | None = None


# 3. Opportunity & Deal Schemas
class OpportunityCreate(CRMBaseModel):
    title: str
    description: str | None = None
    stage: str = "qualification"
    close_date: date


class OpportunityResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    title: str
    description: str | None = None
    stage: str
    close_date: date


class DealCreate(CRMBaseModel):
    opportunity_id: uuid.UUID | None = None
    customer_id: uuid.UUID
    title: str
    amount: float = 0.0
    probability: int = 0
    status: str = "pipeline"


class DealUpdate(CRMBaseModel):
    status: str
    won_lost_reason: str | None = None


class DealResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    opportunity_id: uuid.UUID | None = None
    customer_id: uuid.UUID
    title: str
    amount: float
    probability: int
    status: str
    won_lost_reason: str | None = None


# 4. Quotation & Sales Order Schemas
class QuotationCreate(CRMBaseModel):
    deal_id: uuid.UUID
    total_amount: float = 0.0
    terms: str | None = None
    valid_until: date


class QuotationStatusUpdate(CRMBaseModel):
    status: str  # draft, sent, approved, rejected


class QuotationResponse(CRMBaseModel):
    id: uuid.UUID
    deal_id: uuid.UUID
    version: int
    status: str
    total_amount: float
    terms: str | None = None
    valid_until: date
    file_path: str | None = None


class SalesOrderCreate(CRMBaseModel):
    customer_id: uuid.UUID
    quotation_id: uuid.UUID | None = None
    total_amount: float
    order_date: date


class SalesOrderResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    customer_id: uuid.UUID
    quotation_id: uuid.UUID | None = None
    order_number: str
    total_amount: float
    status: str
    order_date: date


# 5. Activity Schemas
class CRMTaskCreate(CRMBaseModel):
    customer_id: uuid.UUID | None = None
    lead_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    due_date: date
    priority: str = "medium"
    assigned_to_id: uuid.UUID | None = None


class CRMTaskResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    customer_id: uuid.UUID | None = None
    lead_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    due_date: date
    priority: str
    status: str
    assigned_to_id: uuid.UUID | None = None


class MeetingCreate(CRMBaseModel):
    customer_id: uuid.UUID | None = None
    lead_id: uuid.UUID | None = None
    title: str
    scheduled_at: datetime
    duration_minutes: int = 30
    location_or_url: str | None = None


class MeetingResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    customer_id: uuid.UUID | None = None
    lead_id: uuid.UUID | None = None
    title: str
    scheduled_at: datetime
    duration_minutes: int
    location_or_url: str | None = None


# 6. Support Ticket Schemas
class SupportTicketCreate(CRMBaseModel):
    customer_id: uuid.UUID
    category: str = "technical"
    priority: str = "medium"
    assigned_to_id: uuid.UUID | None = None


class SupportTicketUpdate(CRMBaseModel):
    status: str
    resolution_notes: str | None = None


class SupportTicketResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    customer_id: uuid.UUID
    category: str
    priority: str
    status: str
    assigned_to_id: uuid.UUID | None = None
    resolution_notes: str | None = None


# 7. Campaign Schemas
class CampaignCreate(CRMBaseModel):
    name: str
    type: str = "email"
    start_date: date
    end_date: date
    budget: float = 0.0
    expected_revenue: float = 0.0


class CampaignResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    type: str
    status: str
    start_date: date
    end_date: date
    budget: float
    expected_revenue: float
