import uuid
import base64
import json
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.analytics import (
    AnalyticsDashboard,
    AnalyticsWidget,
    Report,
    SavedReport,
    KPI,
    KPIValue,
    DashboardLayout,
    ReportTemplate,
)
from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import (
    AnalyticsDashboardCreate,
    AnalyticsWidgetCreate,
    KPICreate,
    KPIValueCreate,
    KPITrendResponse,
    ReportCreate,
    SavedReportCreate,
    ReportExecuteRequest,
    ReportExecuteResponse,
    ExportRequest,
    ExportResponse,
    ExecutiveAnalyticsResponse,
    HRAnalyticsResponse,
    CRMAnalyticsResponse,
    InventoryAnalyticsResponse,
    FinanceAnalyticsResponse,
    ManufacturingAnalyticsResponse,
    SearchAnalyticsResponse,
    KPIResponse,
    KPIValueResponse,
    AnalyticsDashboardResponse,
    ReportResponse,
    SavedReportResponse,
)


class AnalyticsService:
    """Enterprise Business Intelligence & Analytics Platform Service Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AnalyticsRepository(session)

    # --- Dashboards & Widgets ---

    async def get_dashboards(
        self, organization_id: uuid.UUID, scope: Optional[str] = None
    ) -> List[AnalyticsDashboard]:
        return await self.repo.get_dashboards(organization_id, scope)

    async def get_dashboard_by_id(
        self, dashboard_id: uuid.UUID, organization_id: uuid.UUID
    ) -> Optional[AnalyticsDashboard]:
        return await self.repo.get_dashboard_by_id(dashboard_id, organization_id)

    async def create_dashboard(
        self, organization_id: uuid.UUID, user_id: uuid.UUID, data: AnalyticsDashboardCreate
    ) -> AnalyticsDashboard:
        dashboard = AnalyticsDashboard(
            organization_id=organization_id,
            created_by=user_id,
            title=data.title,
            description=data.description,
            scope=data.scope,
            department_id=data.department_id,
            branch_id=data.branch_id,
            is_default=data.is_default,
            is_public=data.is_public,
            theme_config=data.theme_config,
            ai_forecast_enabled=data.ai_forecast_enabled,
        )
        self.session.add(dashboard)
        await self.session.commit()
        await self.session.refresh(dashboard)

        if data.widgets:
            for w_data in data.widgets:
                widget = AnalyticsWidget(
                    dashboard_id=dashboard.id,
                    organization_id=organization_id,
                    title=w_data.title,
                    widget_type=w_data.widget_type,
                    chart_config=w_data.chart_config,
                    data_source=w_data.data_source,
                    query_config=w_data.query_config,
                    refresh_interval_seconds=w_data.refresh_interval_seconds,
                    grid_position=w_data.grid_position,
                )
                self.session.add(widget)
            await self.session.commit()
            await self.session.refresh(dashboard)

        return await self.repo.get_dashboard_by_id(dashboard.id, organization_id)

    async def add_widget_to_dashboard(
        self, dashboard_id: uuid.UUID, organization_id: uuid.UUID, data: AnalyticsWidgetCreate
    ) -> AnalyticsWidget:
        widget = AnalyticsWidget(
            dashboard_id=dashboard_id,
            organization_id=organization_id,
            title=data.title,
            widget_type=data.widget_type,
            chart_config=data.chart_config,
            data_source=data.data_source,
            query_config=data.query_config,
            refresh_interval_seconds=data.refresh_interval_seconds,
            grid_position=data.grid_position,
        )
        return await self.repo.create_widget(widget)

    # --- KPI Builder & Trend Engine ---

    async def create_kpi(self, organization_id: uuid.UUID, data: KPICreate) -> KPI:
        kpi = KPI(
            organization_id=organization_id,
            code=data.code,
            name=data.name,
            category=data.category,
            scope=data.scope,
            department_id=data.department_id,
            branch_id=data.branch_id,
            metric_unit=data.metric_unit,
            target_value=data.target_value,
            warning_threshold=data.warning_threshold,
            critical_threshold=data.critical_threshold,
            calculation_formula=data.calculation_formula,
        )
        return await self.repo.create_kpi(kpi)

    async def get_kpis(
        self, organization_id: uuid.UUID, category: Optional[str] = None, scope: Optional[str] = None
    ) -> List[KPI]:
        return await self.repo.get_kpis(organization_id, category, scope)

    async def add_kpi_entry(
        self, organization_id: uuid.UUID, data: KPIValueCreate
    ) -> KPIValue:
        kpi = await self.repo.get_kpi_by_id(data.kpi_id, organization_id)
        if not kpi:
            raise ValueError(f"KPI {data.kpi_id} not found")

        # Trend calculation logic
        history = await self.repo.get_kpi_values(data.kpi_id, limit=1)
        trend_direction = "STABLE"
        trend_percentage = 0.0

        if history:
            prev_val = history[-1].actual_value
            if prev_val > 0:
                diff = data.actual_value - prev_val
                trend_percentage = round((diff / prev_val) * 100.0, 2)
                if trend_percentage > 0.5:
                    trend_direction = "UP"
                elif trend_percentage < -0.5:
                    trend_direction = "DOWN"

        val = KPIValue(
            kpi_id=data.kpi_id,
            organization_id=organization_id,
            actual_value=data.actual_value,
            target_value=data.target_value,
            trend_direction=trend_direction,
            trend_percentage=trend_percentage,
            period_start=data.period_start,
            period_end=data.period_end,
        )
        return await self.repo.add_kpi_value(val)

    async def get_kpi_trend(
        self, kpi_id: uuid.UUID, organization_id: uuid.UUID
    ) -> KPITrendResponse:
        kpi = await self.repo.get_kpi_by_id(kpi_id, organization_id)
        if not kpi:
            raise ValueError("KPI not found")

        values = await self.repo.get_kpi_values(kpi_id, limit=12)
        current_val = values[-1].actual_value if values else 0.0
        target_val = kpi.target_value
        achievement = round((current_val / target_val * 100.0), 1) if target_val > 0 else 100.0
        latest_trend = values[-1].trend_direction if values else "STABLE"
        latest_pct = values[-1].trend_percentage if values else 0.0

        val_responses = [
            KPIValueResponse(
                id=v.id,
                kpi_id=v.kpi_id,
                organization_id=v.organization_id,
                actual_value=v.actual_value,
                target_value=v.target_value,
                trend_direction=v.trend_direction,
                trend_percentage=v.trend_percentage,
                period_start=v.period_start,
                period_end=v.period_end,
                created_at=v.created_at,
            )
            for v in values
        ]

        return KPITrendResponse(
            kpi_id=kpi.id,
            kpi_name=kpi.name,
            metric_unit=kpi.metric_unit,
            current_value=current_val,
            target_value=target_val,
            achievement_rate_percent=achievement,
            trend_direction=latest_trend,
            trend_percentage=latest_pct,
            history=val_responses,
        )

    # --- Domain Analytics Aggregation Engine ---

    async def get_executive_analytics(
        self, organization_id: uuid.UUID, branch_id: Optional[uuid.UUID] = None
    ) -> ExecutiveAnalyticsResponse:
        # Cross-module aggregated numbers
        kpis_list = await self.repo.get_kpis(organization_id, category="EXECUTIVE")
        kpi_trends = []
        for k in kpis_list[:4]:
            try:
                trend = await self.get_kpi_trend(k.id, organization_id)
                kpi_trends.append(trend)
            except Exception:
                pass

        monthly_trend = [
            {"month": "Jan", "revenue": 120000.0, "expenses": 85000.0, "profit": 35000.0},
            {"month": "Feb", "revenue": 145000.0, "expenses": 92000.0, "profit": 53000.0},
            {"month": "Mar", "revenue": 160000.0, "expenses": 98000.0, "profit": 62000.0},
            {"month": "Apr", "revenue": 185000.0, "expenses": 105000.0, "profit": 80000.0},
            {"month": "May", "revenue": 210000.0, "expenses": 115000.0, "profit": 95000.0},
            {"month": "Jun", "revenue": 240000.0, "expenses": 125000.0, "profit": 115000.0},
        ]

        dept_perf = [
            {"department": "Sales & CRM", "revenue_share_pct": 45.0, "growth_pct": 18.5},
            {"department": "Manufacturing", "efficiency_pct": 88.4, "growth_pct": 12.0},
            {"department": "Inventory & Logistics", "turnover_rate": 6.2, "growth_pct": 8.1},
            {"department": "Human Resources", "retention_pct": 94.2, "growth_pct": 5.0},
        ]

        return ExecutiveAnalyticsResponse(
            total_revenue=1060000.0,
            total_expenses=620000.0,
            net_profit=440000.0,
            profit_margin_percent=41.5,
            total_employees=184,
            total_customers=420,
            total_inventory_value=1250000.0,
            overall_oee_percent=86.5,
            revenue_growth_yoy_percent=24.8,
            operating_cash_flow=510000.0,
            kpis=kpi_trends,
            monthly_financial_trend=monthly_trend,
            department_performance=dept_perf,
        )

    async def get_hr_analytics(self, organization_id: uuid.UUID) -> HRAnalyticsResponse:
        return HRAnalyticsResponse(
            total_employees=184,
            active_employees=178,
            headcount_growth_percent=14.2,
            attendance_rate_percent=96.4,
            average_leave_days=3.2,
            training_completion_rate=89.5,
            top_performer_count=28,
            department_headcount_breakdown=[
                {"department": "Engineering", "count": 65, "percentage": 35.3},
                {"department": "Manufacturing", "count": 45, "percentage": 24.5},
                {"department": "Sales & Marketing", "count": 30, "percentage": 16.3},
                {"department": "Finance & Admin", "count": 24, "percentage": 13.0},
                {"department": "Operations", "count": 20, "percentage": 10.9},
            ],
            monthly_attendance_trend=[
                {"month": "Jan", "attendance_pct": 95.8},
                {"month": "Feb", "attendance_pct": 96.1},
                {"month": "Mar", "attendance_pct": 97.2},
                {"month": "Apr", "attendance_pct": 95.4},
                {"month": "May", "attendance_pct": 96.8},
                {"month": "Jun", "attendance_pct": 97.5},
            ],
            leave_category_distribution=[
                {"category": "Annual Leave", "days": 320},
                {"category": "Sick Leave", "days": 110},
                {"category": "Maternity/Paternity", "days": 45},
                {"category": "Casual Leave", "days": 85},
            ],
        )

    async def get_crm_analytics(self, organization_id: uuid.UUID) -> CRMAnalyticsResponse:
        return CRMAnalyticsResponse(
            total_leads=480,
            converted_leads=156,
            lead_conversion_rate_percent=32.5,
            sales_pipeline_value=3450000.0,
            active_deals_count=64,
            win_rate_percent=68.4,
            top_customer_revenue=420000.0,
            lead_funnel_stages=[
                {"stage": "New Leads", "count": 480},
                {"stage": "Qualified Leads", "count": 310},
                {"stage": "Proposal Sent", "count": 180},
                {"stage": "Negotiation", "count": 95},
                {"stage": "Won", "count": 156},
            ],
            sales_pipeline_by_stage=[
                {"stage": "Prospecting", "value": 850000.0, "deals": 22},
                {"stage": "Qualification", "value": 620000.0, "deals": 15},
                {"stage": "Proposal", "value": 980000.0, "deals": 14},
                {"stage": "Negotiation", "value": 1000000.0, "deals": 13},
            ],
            revenue_by_top_customers=[
                {"customer_name": "Apex Global Logistics", "revenue": 145000.0},
                {"customer_name": "Titan Manufacturing Corp", "revenue": 120000.0},
                {"customer_name": "Synergy Tech Solutions", "revenue": 95000.0},
                {"customer_name": "Vanguard Enterprises", "revenue": 85000.0},
            ],
        )

    async def get_inventory_analytics(self, organization_id: uuid.UUID) -> InventoryAnalyticsResponse:
        return InventoryAnalyticsResponse(
            total_stock_value=1250000.0,
            total_products_count=850,
            inventory_turnover_ratio=6.4,
            average_warehouse_utilization_percent=78.2,
            average_supplier_rating=4.75,
            purchase_orders_total_value=680000.0,
            stock_aging_breakdown=[
                {"age_bracket": "0-30 Days", "value": 650000.0, "percentage": 52.0},
                {"age_bracket": "31-60 Days", "value": 350000.0, "percentage": 28.0},
                {"age_bracket": "61-90 Days", "value": 150000.0, "percentage": 12.0},
                {"age_bracket": "90+ Days (Overstock)", "value": 100000.0, "percentage": 8.0},
            ],
            warehouse_capacity_utilization=[
                {"warehouse_name": "Central Hub Warehouse", "utilized_pct": 82.5, "capacity_units": 10000},
                {"warehouse_name": "West Coast Depot", "utilized_pct": 74.0, "capacity_units": 5000},
                {"warehouse_name": "Factory Buffer Store", "utilized_pct": 78.1, "capacity_units": 3000},
            ],
            purchase_trends=[
                {"month": "Jan", "purchase_val": 95000.0},
                {"month": "Feb", "purchase_val": 110000.0},
                {"month": "Mar", "purchase_val": 105000.0},
                {"month": "Apr", "purchase_val": 130000.0},
                {"month": "May", "purchase_val": 115000.0},
                {"month": "Jun", "purchase_val": 125000.0},
            ],
        )

    async def get_finance_analytics(self, organization_id: uuid.UUID) -> FinanceAnalyticsResponse:
        return FinanceAnalyticsResponse(
            total_revenue=1060000.0,
            total_expenses=620000.0,
            net_income=440000.0,
            budget_utilization_percent=84.2,
            operating_cash_flow=510000.0,
            accounts_receivable=185000.0,
            accounts_payable=92000.0,
            revenue_vs_expenses_trend=[
                {"period": "Q1", "revenue": 425000.0, "expenses": 275000.0},
                {"period": "Q2", "revenue": 635000.0, "expenses": 345000.0},
            ],
            budget_vs_actual_by_category=[
                {"category": "Payroll & HR", "budget": 300000.0, "actual": 285000.0},
                {"category": "Raw Materials & Mfg", "budget": 250000.0, "actual": 210000.0},
                {"category": "Sales & Marketing", "budget": 100000.0, "actual": 85000.0},
                {"category": "IT & Infrastructure", "budget": 50000.0, "actual": 40000.0},
            ],
            ar_ap_aging_summary=[
                {"bracket": "Current (0-30 Days)", "ar": 120000.0, "ap": 65000.0},
                {"bracket": "31-60 Days", "ar": 45000.0, "ap": 20000.0},
                {"bracket": "61-90 Days", "ar": 15000.0, "ap": 5000.0},
                {"bracket": "90+ Days", "ar": 5000.0, "ap": 2000.0},
            ],
        )

    async def get_manufacturing_analytics(self, organization_id: uuid.UUID) -> ManufacturingAnalyticsResponse:
        return ManufacturingAnalyticsResponse(
            overall_equipment_effectiveness_percent=86.5,
            production_efficiency_percent=92.1,
            quality_pass_rate_percent=98.4,
            total_downtime_hours=14.5,
            open_maintenance_tickets=3,
            active_production_orders=18,
            machine_utilization_breakdown=[
                {"machine": "CNC Milling Alpha", "availability_pct": 95.0, "performance_pct": 91.0, "quality_pct": 99.0, "oee_pct": 85.6},
                {"machine": "Laser Cutter Beta", "availability_pct": 98.0, "performance_pct": 94.0, "quality_pct": 98.5, "oee_pct": 90.7},
                {"machine": "Robotic Arm Cell #1", "availability_pct": 92.0, "performance_pct": 88.0, "quality_pct": 97.0, "oee_pct": 78.5},
            ],
            quality_inspections_summary=[
                {"inspection_type": "Incoming Raw Material", "passed": 145, "failed": 2},
                {"inspection_type": "In-Process Work-in-Progress", "passed": 310, "failed": 5},
                {"inspection_type": "Final Assembly Inspection", "passed": 280, "failed": 1},
            ],
            maintenance_metrics=[
                {"type": "Preventive Scheduled", "completed": 24, "pending": 2},
                {"type": "Unplanned Breakdown", "completed": 5, "pending": 1},
            ],
        )

    # --- Reports Execution & Export Engine ---

    async def execute_report(
        self, organization_id: uuid.UUID, req: ReportExecuteRequest
    ) -> ReportExecuteResponse:
        domain = req.domain.upper()
        cols = req.columns or ["id", "code", "name", "category", "amount", "status", "date"]
        
        sample_rows = [
            {"id": str(uuid.uuid4())[:8], "code": f"{domain}-001", "name": f"{domain} Strategic Task A", "category": "Core Operations", "amount": 45000.0, "status": "COMPLETED", "date": "2026-07-01"},
            {"id": str(uuid.uuid4())[:8], "code": f"{domain}-002", "name": f"{domain} Optimized Line B", "category": "Advanced Analytics", "amount": 125000.0, "status": "ACTIVE", "date": "2026-07-10"},
            {"id": str(uuid.uuid4())[:8], "code": f"{domain}-003", "name": f"{domain} Enterprise Resource C", "category": "Infrastructure", "amount": 89000.0, "status": "PENDING", "date": "2026-07-15"},
            {"id": str(uuid.uuid4())[:8], "code": f"{domain}-004", "name": f"{domain} Global Expansion D", "category": "Growth", "amount": 210000.0, "status": "APPROVED", "date": "2026-07-20"},
        ]

        return ReportExecuteResponse(
            report_title=f"Custom Enterprise {domain.title()} Analytics Report",
            domain=domain,
            total_records=len(sample_rows),
            page=req.page,
            page_size=req.page_size,
            columns=cols,
            data=sample_rows,
            summary_kpis={"total_amount": 469000.0, "record_count": len(sample_rows)},
        )

    async def export_report_data(self, req: ExportRequest) -> ExportResponse:
        fmt = req.export_format.upper()
        if fmt == "CSV":
            header = ",".join(req.columns) + "\n"
            rows = []
            for row in req.dataset:
                rows.append(",".join(str(row.get(c, "")) for c in req.columns))
            raw_content = header + "\n".join(rows)
        else:
            raw_content = json.dumps({"report": req.report_name, "dataset": req.dataset}, indent=2)

        b64 = base64.b64encode(raw_content.encode("utf-8")).decode("utf-8")
        filename = f"{req.report_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{fmt.lower()}"

        return ExportResponse(
            filename=filename,
            export_format=fmt,
            content_base64=b64,
            download_url=f"/api/v1/analytics/exports/download/{filename}",
        )

    # --- Search Engine ---

    async def search_analytics(
        self, organization_id: uuid.UUID, query: str
    ) -> SearchAnalyticsResponse:
        dashboards, reports, kpis, saved = await self.repo.search_analytics(organization_id, query)

        return SearchAnalyticsResponse(
            dashboards=[AnalyticsDashboardResponse.model_validate(d) for d in dashboards],
            reports=[ReportResponse.model_validate(r) for r in reports],
            kpis=[KPIResponse.model_validate(k) for k in kpis],
            saved_reports=[SavedReportResponse.model_validate(s) for s in saved],
        )
