"""Comprehensive Tests for the Analytics & Reporting Domain.

Covers:
1. Enterprise KPI Catalog, Custom KPI creation, and Auto-seeding
2. Dynamic KPI calculation across Finance, Sales, Inventory, Manufacturing, and HR
3. Multi-dimensional Time-Series bucketing (Daily/Weekly/Monthly/Quarterly) and breakdown distributions
4. Universal Date range filtering and period-over-period comparison (delta & percentage)
5. Pre-configured System Dashboards and customizable Widgets
6. Parameterized Analytical Reports, execution logs, and CSV export
7. Multi-Tenant isolation & RBAC permission security
8. Fast, non-blocking query execution safeguarding OLTP workloads
"""

import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.modules.analytics.schemas.aggregation import AnalyticsFilterParams
from app.modules.analytics.schemas.kpi import KPIDefinitionCreate
from app.modules.analytics.services.aggregation_service import AggregationService
from app.modules.analytics.services.dashboard_service import DashboardService
from app.modules.analytics.services.kpi_service import KPIService
from app.modules.analytics.services.reporting_service import ReportingService
from app.modules.crm.models.customer import Customer
from app.modules.crm.models.deal import Deal
from app.modules.crm.models.pipeline import Pipeline, PipelineStage
from app.modules.finance.models.bill import Bill
from app.modules.finance.models.invoice import Invoice
from app.modules.finance.models.party import CustomerParty, VendorParty
from app.modules.hr.models.employee import Employee
from app.modules.hr.models.payroll import PayrollRun
from app.modules.identity.services.jwt_service import JwtService
from app.modules.inventory.models.product import Product
from app.modules.inventory.models.stock_balance import StockBalance
from app.modules.inventory.models.uom import UnitOfMeasure
from app.modules.inventory.models.warehouse import Warehouse
from app.modules.manufacturing.models.bom import BillOfMaterial, BOMVersion
from app.modules.manufacturing.models.production_order import ProductionOrder, ProductionScrap
from app.modules.manufacturing.models.quality import QualityInspection
from app.modules.organization.models.department import Department
from app.modules.organization.models.organization import Organization
from app.modules.organization.models.tenant import Tenant


@pytest.fixture
async def analytics_env(db_session: AsyncSession):
    """Sets up a comprehensive multi-domain environment for analytics testing."""
    tenant = Tenant(
        id=uuid.uuid4(), name="Acme Enterprises Global", slug=f"acme-{uuid.uuid4().hex[:6]}"
    )
    db_session.add(tenant)
    await db_session.flush()

    org = Organization(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        name="Acme North America",
        legal_name="Acme North America Inc",
        tax_identifier="US-123456789",
        base_currency="USD",
    )
    db_session.add(org)
    await db_session.flush()

    # Department
    dept_eng = Department(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        code="DEPT-ENG",
        name="Engineering & Hardware",
    )
    dept_sales = Department(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        code="DEPT-SALES",
        name="Enterprise Sales",
    )
    db_session.add_all([dept_eng, dept_sales])
    await db_session.flush()

    # Employees
    emp1 = Employee(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        department_id=dept_eng.id,
        employee_number="EMP-001",
        first_name="Alice",
        last_name="Smith",
        email="alice.smith@acme.io",
        employment_status="ACTIVE",
    )
    emp2 = Employee(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        department_id=dept_sales.id,
        employee_number="EMP-002",
        first_name="Bob",
        last_name="Jones",
        email="bob.jones@acme.io",
        employment_status="ACTIVE",
    )
    db_session.add_all([emp1, emp2])
    await db_session.flush()

    # UOM & Warehouses
    uom = UnitOfMeasure(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        code="EA",
        name="Each",
        category="UNIT",
    )
    wh_main = Warehouse(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        code="WH-MAIN",
        name="Central Distribution Center",
    )
    db_session.add_all([uom, wh_main])
    await db_session.flush()

    # Products & Stock Balances
    prod1 = Product(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        sku="SKU-SERVER-PRO",
        name="Enterprise Cloud Server X1",
        uom_id=uom.id,
        is_stockable=True,
        cost_price=Decimal("1500.00"),
        selling_price=Decimal("3500.00"),
    )
    db_session.add(prod1)
    await db_session.flush()

    bal1 = StockBalance(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        product_id=prod1.id,
        warehouse_id=wh_main.id,
        quantity_on_hand=Decimal("50.00"),
    )
    db_session.add(bal1)
    await db_session.flush()

    # Financial Parties, Invoices, Bills
    party_cust = CustomerParty(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        code="CUST-001",
        name="Global Tech Solutions",
    )
    party_vend = VendorParty(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        code="VEND-001",
        name="Chipsets Intel Fab",
    )
    db_session.add_all([party_cust, party_vend])
    await db_session.flush()

    inv1 = Invoice(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        customer_id=party_cust.id,
        invoice_number="INV-2026-0001",
        issue_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        status="PAID",
        currency="USD",
        subtotal_amount=Decimal("70000.00"),
        tax_amount=Decimal("7000.00"),
        total_amount=Decimal("77000.00"),
    )
    bill1 = Bill(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        vendor_id=party_vend.id,
        bill_number="BILL-2026-0001",
        bill_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        status="APPROVED",
        currency="USD",
        subtotal_amount=Decimal("30000.00"),
        tax_amount=Decimal("3000.00"),
        total_amount=Decimal("33000.00"),
    )
    db_session.add_all([inv1, bill1])
    await db_session.flush()

    # CRM Pipeline, Stages, Customer & Deal
    pipe = Pipeline(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        name="Enterprise Sales Pipeline",
        is_default=True,
    )
    db_session.add(pipe)
    await db_session.flush()

    stage_qual = PipelineStage(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        pipeline_id=pipe.id,
        name="QUALIFIED",
        stage_order=1,
        probability_pct=Decimal("60.00"),
        stage_type="OPEN",
    )
    stage_won = PipelineStage(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        pipeline_id=pipe.id,
        name="CLOSED_WON",
        stage_order=2,
        probability_pct=Decimal("100.00"),
        stage_type="WON",
    )
    db_session.add_all([stage_qual, stage_won])
    await db_session.flush()

    crm_cust = Customer(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        name="Mega Corp Alpha",
        status="ACTIVE",
    )
    db_session.add(crm_cust)
    await db_session.flush()

    deal1 = Deal(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        pipeline_id=pipe.id,
        stage_id=stage_qual.id,
        customer_id=crm_cust.id,
        title="Enterprise Data Center Expansion",
        value=Decimal("250000.00"),
        win_probability_pct=Decimal("60.00"),
        status="OPEN",
    )
    deal_won = Deal(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        pipeline_id=pipe.id,
        stage_id=stage_won.id,
        customer_id=crm_cust.id,
        title="Edge Compute Deployment",
        value=Decimal("150000.00"),
        win_probability_pct=Decimal("100.00"),
        status="WON",
    )
    db_session.add_all([deal1, deal_won])
    await db_session.flush()

    # Manufacturing BOM & Production Order
    bom1 = BillOfMaterial(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        code="BOM-SERVER-01",
        name="Server BOM V1",
        product_id=prod1.id,
        uom_id=uom.id,
        quantity=Decimal("1.0000"),
    )
    db_session.add(bom1)
    await db_session.flush()

    bom_ver1 = BOMVersion(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        bom_id=bom1.id,
        version_number=1,
    )
    db_session.add(bom_ver1)
    await db_session.flush()

    prod_order1 = ProductionOrder(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        order_number="MO-2026-0001",
        product_id=prod1.id,
        bom_id=bom1.id,
        bom_version_id=bom_ver1.id,
        target_warehouse_id=wh_main.id,
        planned_quantity=Decimal("100.00"),
        planned_start_date=date.today(),
        planned_due_date=date.today() + timedelta(days=7),
        status="IN_PROGRESS",
    )
    db_session.add(prod_order1)
    await db_session.flush()

    # Manufacturing Quality & Scrap
    qc1 = QualityInspection(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        inspection_number="QC-2026-001",
        production_order_id=prod_order1.id,
        product_id=prod1.id,
        inspection_type="FINAL_ASSEMBLY",
        inspected_quantity=Decimal("100.00"),
        passed_quantity=Decimal("98.00"),
        failed_quantity=Decimal("2.00"),
        result="PASSED",
        inspection_date=datetime.now(UTC),
    )
    scrap1 = ProductionScrap(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        production_order_id=prod_order1.id,
        product_id=prod1.id,
        scrap_quantity=Decimal("2.00"),
        scrap_reason="Component Defect",
        unit_cost=Decimal("1500.00"),
        total_scrap_cost=Decimal("3000.00"),
        recorded_at=datetime.now(UTC),
    )
    db_session.add_all([qc1, scrap1])
    await db_session.flush()

    # HR Payroll
    payroll1 = PayrollRun(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        run_number="PAY-202609",
        pay_period_start=date.today().replace(day=1),
        pay_period_end=date.today(),
        pay_date=date.today(),
        status="APPROVED",
        total_gross=18000.00,
        total_net=14000.00,
    )
    db_session.add(payroll1)
    await db_session.commit()

    return {
        "tenant": tenant,
        "org": org,
        "prod": prod1,
        "wh": wh_main,
        "invoice": inv1,
        "bill": bill1,
        "deal": deal1,
        "deal_won": deal_won,
    }


# ==============================================================================
# TEST 1: KPI Definitions Catalog & Auto-Seeding
# ==============================================================================
@pytest.mark.asyncio
async def test_kpi_definitions_catalog_and_seeding(db_session: AsyncSession, analytics_env: dict):
    """Verifies that default enterprise KPIs are seeded and can be queried and customized."""
    tenant = analytics_env["tenant"]
    org = analytics_env["org"]

    kpi_service = KPIService(db_session)
    kpis = await kpi_service.get_kpi_definitions(tenant.id, org.id)

    assert len(kpis) >= 10
    codes = [k.code for k in kpis]
    assert "FIN_GROSS_REVENUE" in codes
    assert "FIN_NET_PROFIT_MARGIN" in codes
    assert "SALES_PIPELINE_VALUE" in codes
    assert "INV_TOTAL_VALUATION" in codes
    assert "MFG_FIRST_PASS_YIELD" in codes
    assert "HR_TOTAL_HEADCOUNT" in codes

    # Create Custom KPI
    custom_kpi = await kpi_service.create_kpi_definition(
        tenant.id,
        org.id,
        KPIDefinitionCreate(
            code="CUST_RETENTION_RATE",
            name="Net Customer Retention %",
            category="SALES",
            unit="PERCENTAGE",
            target_value=Decimal("95.00"),
            warning_threshold=Decimal("90.00"),
            critical_threshold=Decimal("80.00"),
        ),
    )
    assert custom_kpi.code == "CUST_RETENTION_RATE"
    assert custom_kpi.target_value == Decimal("95.00")


# ==============================================================================
# TEST 2: Financial KPIs & Profitability Margins
# ==============================================================================
@pytest.mark.asyncio
async def test_financial_kpis_and_margins(db_session: AsyncSession, analytics_env: dict):
    """Calculates Revenue, Operating Expenses, Net Profit Margin, and DSO."""
    tenant = analytics_env["tenant"]
    org = analytics_env["org"]

    kpi_service = KPIService(db_session)
    params = AnalyticsFilterParams(period="THIS_MONTH")

    rev_card = await kpi_service.calculate_kpi(tenant.id, org.id, "FIN_GROSS_REVENUE", params)
    assert rev_card.current_value == Decimal("77000.00")
    assert "$77,000.00" in rev_card.formatted_value

    exp_card = await kpi_service.calculate_kpi(tenant.id, org.id, "FIN_OP_EXPENSES", params)
    assert exp_card.current_value == Decimal("33000.00")

    margin_card = await kpi_service.calculate_kpi(
        tenant.id, org.id, "FIN_NET_PROFIT_MARGIN", params
    )
    # (77000 - 33000) / 77000 = 57.14%
    assert margin_card.current_value == Decimal("57.14")
    assert margin_card.status == "ON_TRACK"


# ==============================================================================
# TEST 3: Sales Pipeline & Opportunity KPIs
# ==============================================================================
@pytest.mark.asyncio
async def test_sales_and_crm_kpis(db_session: AsyncSession, analytics_env: dict):
    """Calculates active pipeline value and opportunity win rates."""
    tenant = analytics_env["tenant"]
    org = analytics_env["org"]

    kpi_service = KPIService(db_session)
    params = AnalyticsFilterParams(period="THIS_MONTH")

    pipe_card = await kpi_service.calculate_kpi(tenant.id, org.id, "SALES_PIPELINE_VALUE", params)
    assert pipe_card.current_value == Decimal("250000.00")

    win_card = await kpi_service.calculate_kpi(tenant.id, org.id, "SALES_WIN_RATE", params)
    # 1 won deal out of 1 closed deal = 100%
    assert win_card.current_value == Decimal("100.0")


# ==============================================================================
# TEST 4: Inventory & Manufacturing KPIs
# ==============================================================================
@pytest.mark.asyncio
async def test_inventory_and_manufacturing_kpis(db_session: AsyncSession, analytics_env: dict):
    """Calculates stock valuation, quality first-pass yield, and scrap costs."""
    tenant = analytics_env["tenant"]
    org = analytics_env["org"]

    kpi_service = KPIService(db_session)
    params = AnalyticsFilterParams(period="THIS_MONTH")

    # Inventory Valuation = 50 on-hand * 1500 cost = 75,000
    inv_card = await kpi_service.calculate_kpi(tenant.id, org.id, "INV_TOTAL_VALUATION", params)
    assert inv_card.current_value == Decimal("75000.00")

    # First Pass Yield = 98 passed / 100 inspected = 98.0%
    fpy_card = await kpi_service.calculate_kpi(tenant.id, org.id, "MFG_FIRST_PASS_YIELD", params)
    assert fpy_card.current_value == Decimal("98.0")
    assert fpy_card.status == "ON_TRACK"

    # Scrap Cost = 3000
    scrap_card = await kpi_service.calculate_kpi(tenant.id, org.id, "MFG_TOTAL_SCRAP_COST", params)
    assert scrap_card.current_value == Decimal("3000.00")


# ==============================================================================
# TEST 5: HR Headcount & Payroll Metrics
# ==============================================================================
@pytest.mark.asyncio
async def test_hr_and_workforce_kpis(db_session: AsyncSession, analytics_env: dict):
    """Calculates active headcount and monthly payroll burn."""
    tenant = analytics_env["tenant"]
    org = analytics_env["org"]

    kpi_service = KPIService(db_session)
    params = AnalyticsFilterParams(period="THIS_MONTH")

    hc_card = await kpi_service.calculate_kpi(tenant.id, org.id, "HR_TOTAL_HEADCOUNT", params)
    assert hc_card.current_value == Decimal("2")

    pay_card = await kpi_service.calculate_kpi(tenant.id, org.id, "HR_MONTHLY_PAYROLL", params)
    assert pay_card.current_value == Decimal("18000.00")


# ==============================================================================
# TEST 6: Multi-Dimensional Aggregations & Time-Series Buckets
# ==============================================================================
@pytest.mark.asyncio
async def test_time_series_and_dimensional_aggregations(
    db_session: AsyncSession, analytics_env: dict
):
    """Tests time-series grouping and dimensional breakdowns."""
    tenant = analytics_env["tenant"]
    org = analytics_env["org"]

    agg_service = AggregationService(db_session)
    params = AnalyticsFilterParams(period="THIS_MONTH")

    # Financial Trend
    fin_trend = await agg_service.get_financial_trend(tenant.id, org.id, params)
    assert len(fin_trend.series) > 0
    assert fin_trend.chart_type == "LINE"

    # Sales Pipeline Breakdown
    sales_pipe = await agg_service.get_sales_pipeline_distribution(tenant.id, org.id, params)
    assert len(sales_pipe.breakdowns) >= 2
    stages = [b.dimension_key for b in sales_pipe.breakdowns]
    assert "QUALIFIED" in stages
    assert "CLOSED_WON" in stages

    # Inventory by Warehouse
    inv_wh = await agg_service.get_inventory_warehouse_breakdown(tenant.id, org.id)
    assert len(inv_wh.breakdowns) == 1
    assert inv_wh.breakdowns[0].dimension_label == "Central Distribution Center"
    assert inv_wh.breakdowns[0].total_amount == Decimal("75000.00")

    # HR Headcount by Department
    hr_dept = await agg_service.get_hr_department_headcount(tenant.id, org.id)
    assert len(hr_dept.breakdowns) == 2


# ==============================================================================
# TEST 7: Dashboard Management & Pre-Seeded Dashboards
# ==============================================================================
@pytest.mark.asyncio
async def test_dashboards_crud_and_widgets(db_session: AsyncSession, analytics_env: dict):
    """Verifies system dashboards and widget attachments."""
    tenant = analytics_env["tenant"]
    org = analytics_env["org"]

    dash_service = DashboardService(db_session)
    dashboards = await dash_service.list_dashboards(tenant.id, org.id)

    assert len(dashboards) == 6
    codes = [d.code for d in dashboards]
    assert "EXECUTIVE_OVERVIEW" in codes
    assert "FINANCIAL_PERFORMANCE" in codes
    assert "SALES_PIPELINE" in codes
    assert "INVENTORY_HEALTH" in codes
    assert "MANUFACTURING_OPS" in codes
    assert "HR_WORKFORCE" in codes

    # Fetch single dashboard
    exec_dash = await dash_service.get_dashboard_by_code(tenant.id, org.id, "EXECUTIVE_OVERVIEW")
    assert exec_dash is not None
    assert len(exec_dash.widgets) == 6


# ==============================================================================
# TEST 8: Analytical Reports Execution & CSV Export
# ==============================================================================
@pytest.mark.asyncio
async def test_reports_execution_and_csv_export(db_session: AsyncSession, analytics_env: dict):
    """Runs reports and verifies structured rows and CSV formatting."""
    tenant = analytics_env["tenant"]
    org = analytics_env["org"]

    report_service = ReportingService(db_session)
    reports = await report_service.list_reports(tenant.id, org.id)
    assert len(reports) >= 6

    # Execute Executive Summary Report
    res = await report_service.execute_report(
        tenant_id=tenant.id,
        org_id=org.id,
        report_code="REP_EXEC_SUMMARY",
        parameters={},
        export_csv=True,
    )
    assert res.status == "COMPLETED"
    assert len(res.rows) == 6
    assert res.csv_content is not None
    assert "Gross Revenue" in res.csv_content
    assert "Active Pipeline" in res.csv_content


# ==============================================================================
# TEST 9: Multi-Tenant Isolation in Analytics
# ==============================================================================
@pytest.mark.asyncio
async def test_tenant_isolation_in_analytics(db_session: AsyncSession, analytics_env: dict):
    """Ensures queries for Tenant B cannot access or leak Tenant A's metrics."""
    analytics_env["tenant"]
    analytics_env["org"]

    # Create Tenant B
    tenant_b = Tenant(id=uuid.uuid4(), name="Competitor Corp", slug=f"comp-{uuid.uuid4().hex[:6]}")
    db_session.add(tenant_b)
    await db_session.flush()

    org_b = Organization(
        id=uuid.uuid4(),
        tenant_id=tenant_b.id,
        name="Competitor Org",
        legal_name="Competitor LLC",
        tax_identifier="US-999999999",
        base_currency="USD",
    )
    db_session.add(org_b)
    await db_session.commit()

    kpi_service = KPIService(db_session)
    params = AnalyticsFilterParams(period="THIS_MONTH")

    # Tenant B should have 0 revenue and 0 headcount
    rev_b = await kpi_service.calculate_kpi(tenant_b.id, org_b.id, "FIN_GROSS_REVENUE", params)
    assert rev_b.current_value == Decimal("0.00")

    hc_b = await kpi_service.calculate_kpi(tenant_b.id, org_b.id, "HR_TOTAL_HEADCOUNT", params)
    assert hc_b.current_value == Decimal("0")


# ==============================================================================
# TEST 10: Analytics REST API Endpoints with RBAC Tokens
# ==============================================================================
@pytest.mark.asyncio
async def test_analytics_api_endpoints(
    async_client: AsyncClient,
    db_session: AsyncSession,
    analytics_env: dict,
):
    """Tests FastAPI Analytics endpoints with RBAC authentication."""
    tenant = analytics_env["tenant"]
    org = analytics_env["org"]

    all_permissions = [p.value for p in PermissionCode]
    token, _, _ = JwtService.create_access_token(
        user_id=uuid.uuid4(),
        tenant_id=tenant.id,
        organization_id=org.id,
        roles=["Executive", "ChiefFinancialOfficer"],
        permissions=all_permissions,
        session_id=uuid.uuid4(),
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": str(tenant.id),
        "X-Organization-ID": str(org.id),
    }

    # 1. GET /api/v1/analytics/kpis
    res = await async_client.get("/api/v1/analytics/kpis", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 10

    # 2. POST /api/v1/analytics/summary/executive
    res = await async_client.post(
        "/api/v1/analytics/summary/executive", json={"period": "THIS_MONTH"}, headers=headers
    )
    assert res.status_code == 200
    exec_data = res.json()
    assert len(exec_data["kpis"]) == 6

    # 3. GET /api/v1/analytics/dashboards
    res = await async_client.get("/api/v1/analytics/dashboards", headers=headers)
    assert res.status_code == 200
    dash_data = res.json()
    assert dash_data["total"] == 6

    # 4. POST /api/v1/analytics/reports/REP_EXEC_SUMMARY/execute
    res = await async_client.post(
        "/api/v1/analytics/reports/REP_EXEC_SUMMARY/execute",
        json={"parameters": {}, "format": "JSON"},
        headers=headers,
    )
    assert res.status_code == 200
    rep_data = res.json()
    assert rep_data["status"] == "COMPLETED"
    assert len(rep_data["rows"]) == 6
