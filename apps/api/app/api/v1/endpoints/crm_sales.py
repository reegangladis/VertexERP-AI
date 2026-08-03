import uuid
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_db_session
from app.models.user import User
from app.repositories.crm_sales import (
    CRMTaskRepository,
    CustomerContactRepository,
    CustomerRepository,
    CustomerTimelineRepository,
    LeadRepository,
    LeadSourceRepository,
    MeetingRepository,
    OpportunityRepository,
    QuotationRepository,
    SalesOrderRepository,
)
from app.schemas.crm_sales import (
    CRMTaskCreate,
    CRMTaskResponse,
    CRMTaskUpdate,
    CRMDashboardSummary,
    CustomerAddressCreate,
    CustomerAddressResponse,
    CustomerContactCreate,
    CustomerContactResponse,
    CustomerContactUpdate,
    CustomerCreate,
    CustomerResponse,
    CustomerTimelineResponse,
    CustomerUpdate,
    LeadActivityResponse,
    LeadAssignPayload,
    LeadConvertPayload,
    LeadCreate,
    LeadResponse,
    LeadSourceCreate,
    LeadSourceResponse,
    LeadUpdate,
    MeetingCreate,
    MeetingResponse,
    MeetingUpdate,
    OpportunityCreate,
    OpportunityResponse,
    OpportunityUpdate,
    QuotationCreate,
    QuotationResponse,
    QuotationUpdate,
    SalesOrderCreate,
    SalesOrderResponse,
    SalesOrderUpdate,
)
from app.services.crm_sales import (
    CRMAnalyticsService,
    CustomerService,
    LeadService,
    OpportunityService,
    QuotationService,
    SalesOrderService,
)

router = APIRouter()


# --- Lead Sources ---
@router.post("/lead-sources", response_model=LeadSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_lead_source(
    payload: LeadSourceCreate,
    current_user: User = Depends(PermissionChecker("lead.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = LeadSourceRepository(db)
    return await repo.create(payload.model_dump())


@router.get("/lead-sources", response_model=list[LeadSourceResponse])
async def list_lead_sources(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("crm.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = LeadSourceRepository(db)
    return await repo.get_by_org(org_id)


# --- Leads ---
@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    payload: LeadCreate,
    current_user: User = Depends(PermissionChecker("lead.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = LeadService(db)
    return await service.create_lead(payload)


@router.get("/leads", response_model=list[LeadResponse])
async def list_leads(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("crm.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = LeadRepository(db)
    return await repo.get_by_org(org_id)


@router.get("/leads/{id}", response_model=LeadResponse)
async def get_lead(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("crm.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = LeadRepository(db)
    lead = await repo.get_with_activities(id)
    if not lead:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return lead


@router.put("/leads/{id}", response_model=LeadResponse)
async def update_lead(
    id: uuid.UUID,
    payload: LeadUpdate,
    current_user: User = Depends(PermissionChecker("lead.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = LeadService(db)
    return await service.update_lead(id, payload)


@router.post("/leads/{id}/assign", response_model=LeadResponse)
async def assign_lead(
    id: uuid.UUID,
    payload: LeadAssignPayload,
    current_user: User = Depends(PermissionChecker("lead.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = LeadService(db)
    return await service.assign_lead(id, payload)


@router.post("/leads/{id}/convert", response_model=CustomerResponse)
async def convert_lead(
    id: uuid.UUID,
    payload: LeadConvertPayload,
    current_user: User = Depends(PermissionChecker("lead.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = LeadService(db)
    return await service.convert_lead(id, payload)


@router.delete("/leads/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("crm.delete")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = LeadRepository(db)
    await repo.delete(id)
    return None


# --- Customers & Contacts ---
@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate,
    current_user: User = Depends(PermissionChecker("customer.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = CustomerService(db)
    return await service.create_customer(payload)


@router.get("/customers", response_model=list[CustomerResponse])
async def list_customers(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("crm.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = CustomerRepository(db)
    records, _ = await repo.get_multi(filters={"organization_id": org_id})
    return records


@router.get("/customers/{id}", response_model=CustomerResponse)
async def get_customer(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("crm.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = CustomerRepository(db)
    customer = await repo.get_with_details(id)
    if not customer:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return customer


@router.post("/customer-contacts", response_model=CustomerContactResponse, status_code=status.HTTP_201_CREATED)
async def add_customer_contact(
    payload: CustomerContactCreate,
    current_user: User = Depends(PermissionChecker("customer.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = CustomerService(db)
    return await service.add_contact(payload)


@router.get("/customer-contacts", response_model=list[CustomerContactResponse])
async def list_customer_contacts(
    customer_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("crm.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = CustomerContactRepository(db)
    return await repo.get_by_customer(customer_id)


@router.get("/customer-timeline", response_model=list[CustomerTimelineResponse])
async def get_customer_timeline(
    customer_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("crm.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = CustomerTimelineRepository(db)
    return await repo.get_by_customer(customer_id)


# --- Opportunities & Sales Pipeline ---
@router.post("/opportunities", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    payload: OpportunityCreate,
    current_user: User = Depends(PermissionChecker("sales.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = OpportunityService(db)
    return await service.create_opportunity(payload)


@router.get("/opportunities", response_model=list[OpportunityResponse])
async def list_opportunities(
    customer_id: uuid.UUID | None = None,
    current_user: User = Depends(PermissionChecker("crm.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = OpportunityRepository(db)
    if customer_id:
        return await repo.get_by_customer(customer_id)
    records, _ = await repo.get_multi()
    return records


@router.put("/opportunities/{id}", response_model=OpportunityResponse)
async def update_opportunity(
    id: uuid.UUID,
    payload: OpportunityUpdate,
    current_user: User = Depends(PermissionChecker("sales.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = OpportunityService(db)
    return await service.update_opportunity(id, payload)


# --- Quotations ---
@router.post("/quotations", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
async def create_quotation(
    payload: QuotationCreate,
    current_user: User = Depends(PermissionChecker("quotation.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = QuotationService(db)
    return await service.create_quotation(payload)


@router.get("/quotations", response_model=list[QuotationResponse])
async def list_quotations(
    customer_id: uuid.UUID | None = None,
    current_user: User = Depends(PermissionChecker("crm.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = QuotationRepository(db)
    records, _ = await repo.get_multi(filters={"customer_id": customer_id} if customer_id else None)
    return records


@router.get("/quotations/{quotation_number}/download-pdf")
async def download_quotation_pdf(
    quotation_number: str,
    current_user: User = Depends(PermissionChecker("crm.read")),
    db: AsyncSession = Depends(get_db_session),
):
    service = QuotationService(db)
    pdf_content = await service.generate_pdf_text(quotation_number)
    return Response(
        content=pdf_content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="Quotation_{quotation_number}.txt"'},
    )


# --- Sales Orders ---
@router.post("/sales-orders", response_model=SalesOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_sales_order(
    payload: SalesOrderCreate,
    current_user: User = Depends(PermissionChecker("sales.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = SalesOrderService(db)
    return await service.create_sales_order(payload)


@router.get("/sales-orders", response_model=list[SalesOrderResponse])
async def list_sales_orders(
    customer_id: uuid.UUID | None = None,
    current_user: User = Depends(PermissionChecker("crm.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = SalesOrderRepository(db)
    records, _ = await repo.get_multi(filters={"customer_id": customer_id} if customer_id else None)
    return records


# --- CRM Tasks & Meetings ---
@router.post("/crm-tasks", response_model=CRMTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_crm_task(
    payload: CRMTaskCreate,
    current_user: User = Depends(PermissionChecker("crm.create")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = CRMTaskRepository(db)
    return await repo.create(payload.model_dump())


@router.get("/crm-tasks", response_model=list[CRMTaskResponse])
async def list_crm_tasks(
    current_user: User = Depends(PermissionChecker("crm.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = CRMTaskRepository(db)
    records, _ = await repo.get_multi()
    return records


@router.post("/meetings", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    payload: MeetingCreate,
    current_user: User = Depends(PermissionChecker("crm.create")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = MeetingRepository(db)
    return await repo.create(payload.model_dump())


@router.get("/meetings", response_model=list[MeetingResponse])
async def list_meetings(
    current_user: User = Depends(PermissionChecker("crm.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = MeetingRepository(db)
    records, _ = await repo.get_multi()
    return records


# --- CRM Analytics & Dashboard ---
@router.get("/crm/dashboard", response_model=CRMDashboardSummary)
async def get_crm_dashboard(
    org_id: uuid.UUID = Query(...),
    customer_id: uuid.UUID | None = None,
    current_user: User = Depends(PermissionChecker("crm.read")),
    db: AsyncSession = Depends(get_db_session),
):
    service = CRMAnalyticsService(db)
    return await service.get_dashboard_summary(org_id, customer_id)
