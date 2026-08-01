import uuid
from datetime import date, datetime
from typing import List, Optional, Any
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
    phone: Optional[str] = None
    company: Optional[str] = None
    status: str = "new"
    lead_source_id: Optional[uuid.UUID] = None
    assigned_to_id: Optional[uuid.UUID] = None

class LeadUpdate(CRMBaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    status: Optional[str] = None
    assigned_to_id: Optional[uuid.UUID] = None

class LeadResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    status: str
    lead_source_id: Optional[uuid.UUID] = None
    score: int
    assigned_to_id: Optional[uuid.UUID] = None

class LeadConvertRequest(CRMBaseModel):
    customer_name: Optional[str] = None
    create_opportunity: bool = True
    opportunity_title: Optional[str] = None
    deal_amount: Optional[float] = 0.0

# 2. Customer & Contact Schemas
class ContactCreate(CRMBaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    is_primary: bool = False

class ContactResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    customer_id: Optional[uuid.UUID] = None
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    is_primary: bool

class CustomerCreate(CRMBaseModel):
    type: str = "business"
    name: str
    industry: Optional[str] = None
    status: str = "active"
    communication_preferences: Optional[dict] = None
    tags: Optional[List[str]] = None
    contacts: Optional[List[ContactCreate]] = None

class CustomerUpdate(CRMBaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None

class CustomerResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    type: str
    name: str
    industry: Optional[str] = None
    status: str
    communication_preferences: Optional[dict] = None
    tags: Optional[dict] = None

# 3. Opportunity & Deal Schemas
class OpportunityCreate(CRMBaseModel):
    title: str
    description: Optional[str] = None
    stage: str = "qualification"
    close_date: date

class OpportunityResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    title: str
    description: Optional[str] = None
    stage: str
    close_date: date

class DealCreate(CRMBaseModel):
    opportunity_id: Optional[uuid.UUID] = None
    customer_id: uuid.UUID
    title: str
    amount: float = 0.0
    probability: int = 0
    status: str = "pipeline"

class DealUpdate(CRMBaseModel):
    status: str
    won_lost_reason: Optional[str] = None

class DealResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    opportunity_id: Optional[uuid.UUID] = None
    customer_id: uuid.UUID
    title: str
    amount: float
    probability: int
    status: str
    won_lost_reason: Optional[str] = None

# 4. Quotation & Sales Order Schemas
class QuotationCreate(CRMBaseModel):
    deal_id: uuid.UUID
    total_amount: float = 0.0
    terms: Optional[str] = None
    valid_until: date

class QuotationStatusUpdate(CRMBaseModel):
    status: str # draft, sent, approved, rejected

class QuotationResponse(CRMBaseModel):
    id: uuid.UUID
    deal_id: uuid.UUID
    version: int
    status: str
    total_amount: float
    terms: Optional[str] = None
    valid_until: date
    file_path: Optional[str] = None

class SalesOrderCreate(CRMBaseModel):
    customer_id: uuid.UUID
    quotation_id: Optional[uuid.UUID] = None
    total_amount: float
    order_date: date

class SalesOrderResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    customer_id: uuid.UUID
    quotation_id: Optional[uuid.UUID] = None
    order_number: str
    total_amount: float
    status: str
    order_date: date

# 5. Activity Schemas
class CRMTaskCreate(CRMBaseModel):
    customer_id: Optional[uuid.UUID] = None
    lead_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    due_date: date
    priority: str = "medium"
    assigned_to_id: Optional[uuid.UUID] = None

class CRMTaskResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    customer_id: Optional[uuid.UUID] = None
    lead_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    due_date: date
    priority: str
    status: str
    assigned_to_id: Optional[uuid.UUID] = None

class MeetingCreate(CRMBaseModel):
    customer_id: Optional[uuid.UUID] = None
    lead_id: Optional[uuid.UUID] = None
    title: str
    scheduled_at: datetime
    duration_minutes: int = 30
    location_or_url: Optional[str] = None

class MeetingResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    customer_id: Optional[uuid.UUID] = None
    lead_id: Optional[uuid.UUID] = None
    title: str
    scheduled_at: datetime
    duration_minutes: int
    location_or_url: Optional[str] = None

# 6. Support Ticket Schemas
class SupportTicketCreate(CRMBaseModel):
    customer_id: uuid.UUID
    category: str = "technical"
    priority: str = "medium"
    assigned_to_id: Optional[uuid.UUID] = None

class SupportTicketUpdate(CRMBaseModel):
    status: str
    resolution_notes: Optional[str] = None

class SupportTicketResponse(CRMBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    customer_id: uuid.UUID
    category: str
    priority: str
    status: str
    assigned_to_id: Optional[uuid.UUID] = None
    resolution_notes: Optional[str] = None

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
