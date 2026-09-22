"""Analytics Dashboard and Widget Management Service."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.models.dashboard import Dashboard, DashboardWidget
from app.modules.analytics.schemas.dashboard import (
    DashboardCreate,
)


class DashboardService:
    """Service for managing customizable and system enterprise dashboards."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_dashboards(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        category: str | None = None,
    ) -> list[Dashboard]:
        """List dashboards for tenant and organization, auto-seeding defaults if empty."""
        stmt = select(Dashboard).where(
            Dashboard.tenant_id == tenant_id,
            Dashboard.organization_id == org_id,
        )
        if category:
            stmt = stmt.where(Dashboard.category == category)
        stmt = stmt.order_by(Dashboard.is_default.desc(), Dashboard.name)

        res = await self.session.execute(stmt)
        dashboards = list(res.scalars().all())

        if not dashboards and not category:
            await self.seed_default_dashboards(tenant_id, org_id)
            res = await self.session.execute(stmt)
            dashboards = list(res.scalars().all())

        return dashboards

    async def get_dashboard_by_code(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        code: str,
    ) -> Dashboard | None:
        """Fetch dashboard by unique code."""
        stmt = select(Dashboard).where(
            Dashboard.tenant_id == tenant_id,
            Dashboard.organization_id == org_id,
            Dashboard.code == code,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_dashboard(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        data: DashboardCreate,
        user_id: uuid.UUID | None = None,
    ) -> Dashboard:
        """Create a custom dashboard with widgets."""
        dash = Dashboard(
            tenant_id=tenant_id,
            organization_id=data.organization_id or org_id,
            code=data.code.upper(),
            name=data.name,
            category=data.category,
            description=data.description,
            layout_config=data.layout_config,
            is_default=data.is_default,
            is_system=data.is_system,
            required_permission=data.required_permission,
            created_by_id=user_id,
        )
        self.session.add(dash)
        await self.session.flush()

        for w in data.widgets:
            widget = DashboardWidget(
                tenant_id=tenant_id,
                dashboard_id=dash.id,
                title=w.title,
                widget_type=w.widget_type,
                kpi_code=w.kpi_code,
                data_source=w.data_source,
                query_config=w.query_config,
                grid_x=w.grid_x,
                grid_y=w.grid_y,
                grid_w=w.grid_w,
                grid_h=w.grid_h,
                sort_order=w.sort_order,
            )
            self.session.add(widget)

        await self.session.commit()
        await self.session.refresh(dash)
        return dash

    async def seed_default_dashboards(self, tenant_id: uuid.UUID, org_id: uuid.UUID) -> None:
        """Pre-seeds 6 pre-configured enterprise system dashboards."""
        dashboards_data = [
            # 1. Executive
            {
                "code": "EXECUTIVE_OVERVIEW",
                "name": "Executive Enterprise Overview",
                "category": "EXECUTIVE",
                "description": "Consolidated C-Suite overview with revenue, margins, pipeline, stock valuation, and headcount.",
                "is_default": True,
                "is_system": True,
                "required_permission": "analytics:dashboards:read",
                "widgets": [
                    {
                        "title": "Gross Revenue",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "FIN_GROSS_REVENUE",
                        "data_source": "KPI_CARD",
                        "grid_x": 0,
                        "grid_y": 0,
                        "grid_w": 3,
                        "grid_h": 2,
                    },
                    {
                        "title": "Net Profit Margin",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "FIN_NET_PROFIT_MARGIN",
                        "data_source": "KPI_CARD",
                        "grid_x": 3,
                        "grid_y": 0,
                        "grid_w": 3,
                        "grid_h": 2,
                    },
                    {
                        "title": "Active Pipeline",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "SALES_PIPELINE_VALUE",
                        "data_source": "KPI_CARD",
                        "grid_x": 6,
                        "grid_y": 0,
                        "grid_w": 3,
                        "grid_h": 2,
                    },
                    {
                        "title": "Active Headcount",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "HR_TOTAL_HEADCOUNT",
                        "data_source": "KPI_CARD",
                        "grid_x": 9,
                        "grid_y": 0,
                        "grid_w": 3,
                        "grid_h": 2,
                    },
                    {
                        "title": "Revenue vs Expenses Trend",
                        "widget_type": "LINE_CHART",
                        "data_source": "FINANCIAL_TREND",
                        "grid_x": 0,
                        "grid_y": 2,
                        "grid_w": 8,
                        "grid_h": 4,
                    },
                    {
                        "title": "Pipeline Stage Distribution",
                        "widget_type": "DONUT_CHART",
                        "data_source": "SALES_PIPELINE",
                        "grid_x": 8,
                        "grid_y": 2,
                        "grid_w": 4,
                        "grid_h": 4,
                    },
                ],
            },
            # 2. Finance
            {
                "code": "FINANCIAL_PERFORMANCE",
                "name": "Financial Health & Profitability",
                "category": "FINANCE",
                "description": "Profit margins, revenue streams, OPEX breakdown, and working capital turnover.",
                "is_default": False,
                "is_system": True,
                "required_permission": "analytics:finance:read",
                "widgets": [
                    {
                        "title": "Gross Revenue",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "FIN_GROSS_REVENUE",
                        "data_source": "KPI_CARD",
                        "grid_x": 0,
                        "grid_y": 0,
                        "grid_w": 3,
                        "grid_h": 2,
                    },
                    {
                        "title": "Operating Expenses",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "FIN_OP_EXPENSES",
                        "data_source": "KPI_CARD",
                        "grid_x": 3,
                        "grid_y": 0,
                        "grid_w": 3,
                        "grid_h": 2,
                    },
                    {
                        "title": "Net Margin %",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "FIN_NET_PROFIT_MARGIN",
                        "data_source": "KPI_CARD",
                        "grid_x": 6,
                        "grid_y": 0,
                        "grid_w": 3,
                        "grid_h": 2,
                    },
                    {
                        "title": "Days Sales Outstanding",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "FIN_DSO",
                        "data_source": "KPI_CARD",
                        "grid_x": 9,
                        "grid_y": 0,
                        "grid_w": 3,
                        "grid_h": 2,
                    },
                ],
            },
            # 3. Sales
            {
                "code": "SALES_PIPELINE",
                "name": "Sales Velocity & Pipeline",
                "category": "SALES",
                "description": "Opportunity pipeline value, deal conversions, win rates, and booking milestones.",
                "is_default": False,
                "is_system": True,
                "required_permission": "analytics:sales:read",
                "widgets": [
                    {
                        "title": "Pipeline Value",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "SALES_PIPELINE_VALUE",
                        "data_source": "KPI_CARD",
                        "grid_x": 0,
                        "grid_y": 0,
                        "grid_w": 4,
                        "grid_h": 2,
                    },
                    {
                        "title": "Win Rate %",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "SALES_WIN_RATE",
                        "data_source": "KPI_CARD",
                        "grid_x": 4,
                        "grid_y": 0,
                        "grid_w": 4,
                        "grid_h": 2,
                    },
                    {
                        "title": "Total Bookings",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "SALES_TOTAL_BOOKINGS",
                        "data_source": "KPI_CARD",
                        "grid_x": 8,
                        "grid_y": 0,
                        "grid_w": 4,
                        "grid_h": 2,
                    },
                ],
            },
            # 4. Inventory
            {
                "code": "INVENTORY_HEALTH",
                "name": "Inventory & Supply Chain",
                "category": "INVENTORY",
                "description": "Stock valuation, turnover velocity, warehouse distribution, and stockout prevention.",
                "is_default": False,
                "is_system": True,
                "required_permission": "analytics:inventory:read",
                "widgets": [
                    {
                        "title": "Stock Valuation",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "INV_TOTAL_VALUATION",
                        "data_source": "KPI_CARD",
                        "grid_x": 0,
                        "grid_y": 0,
                        "grid_w": 4,
                        "grid_h": 2,
                    },
                    {
                        "title": "Inventory Turns",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "INV_TURNOVER_RATIO",
                        "data_source": "KPI_CARD",
                        "grid_x": 4,
                        "grid_y": 0,
                        "grid_w": 4,
                        "grid_h": 2,
                    },
                    {
                        "title": "Stockout Rate %",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "INV_STOCKOUT_RATE",
                        "data_source": "KPI_CARD",
                        "grid_x": 8,
                        "grid_y": 0,
                        "grid_w": 4,
                        "grid_h": 2,
                    },
                ],
            },
            # 5. Manufacturing
            {
                "code": "MANUFACTURING_OPS",
                "name": "Manufacturing Efficiency",
                "category": "MANUFACTURING",
                "description": "First-pass quality yield, scrap costs, order completion rates, and production volume.",
                "is_default": False,
                "is_system": True,
                "required_permission": "analytics:manufacturing:read",
                "widgets": [
                    {
                        "title": "First-Pass Yield",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "MFG_FIRST_PASS_YIELD",
                        "data_source": "KPI_CARD",
                        "grid_x": 0,
                        "grid_y": 0,
                        "grid_w": 4,
                        "grid_h": 2,
                    },
                    {
                        "title": "Scrap & Loss Cost",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "MFG_TOTAL_SCRAP_COST",
                        "data_source": "KPI_CARD",
                        "grid_x": 4,
                        "grid_y": 0,
                        "grid_w": 4,
                        "grid_h": 2,
                    },
                    {
                        "title": "Order Completion",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "MFG_ORDER_COMPLETION_RATE",
                        "data_source": "KPI_CARD",
                        "grid_x": 8,
                        "grid_y": 0,
                        "grid_w": 4,
                        "grid_h": 2,
                    },
                ],
            },
            # 6. HR
            {
                "code": "HR_WORKFORCE",
                "name": "Human Capital & Workforce",
                "category": "HR",
                "description": "Headcount trends, compensation burn, attrition metrics, and attendance adherence.",
                "is_default": False,
                "is_system": True,
                "required_permission": "analytics:hr:read",
                "widgets": [
                    {
                        "title": "Active Headcount",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "HR_TOTAL_HEADCOUNT",
                        "data_source": "KPI_CARD",
                        "grid_x": 0,
                        "grid_y": 0,
                        "grid_w": 4,
                        "grid_h": 2,
                    },
                    {
                        "title": "Monthly Payroll Burn",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "HR_MONTHLY_PAYROLL",
                        "data_source": "KPI_CARD",
                        "grid_x": 4,
                        "grid_y": 0,
                        "grid_w": 4,
                        "grid_h": 2,
                    },
                    {
                        "title": "Turnover Rate %",
                        "widget_type": "METRIC_CARD",
                        "kpi_code": "HR_TURNOVER_RATE",
                        "data_source": "KPI_CARD",
                        "grid_x": 8,
                        "grid_y": 0,
                        "grid_w": 4,
                        "grid_h": 2,
                    },
                ],
            },
        ]

        for d in dashboards_data:
            dash = Dashboard(
                tenant_id=tenant_id,
                organization_id=org_id,
                code=d["code"],
                name=d["name"],
                category=d["category"],
                description=d["description"],
                is_default=d["is_default"],
                is_system=d["is_system"],
                required_permission=d["required_permission"],
            )
            self.session.add(dash)
            await self.session.flush()

            for idx, w in enumerate(d["widgets"]):
                widget = DashboardWidget(
                    tenant_id=tenant_id,
                    dashboard_id=dash.id,
                    title=w["title"],
                    widget_type=w["widget_type"],
                    kpi_code=w.get("kpi_code"),
                    data_source=w["data_source"],
                    grid_x=w["grid_x"],
                    grid_y=w["grid_y"],
                    grid_w=w["grid_w"],
                    grid_h=w["grid_h"],
                    sort_order=idx,
                )
                self.session.add(widget)

        await self.session.commit()
