"""Analytics Aggregation Service for time-series bucketing and dimensional slicing."""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.schemas.aggregation import (
    AnalyticsFilterParams,
    ChartDatasetResponse,
    DimensionalBucket,
    TimeSeriesPoint,
)
from app.modules.analytics.services.kpi_service import KPIService
from app.modules.crm.models.deal import Deal
from app.modules.crm.models.pipeline import PipelineStage
from app.modules.finance.models.bill import Bill
from app.modules.finance.models.invoice import Invoice
from app.modules.hr.models.employee import Employee
from app.modules.inventory.models.product import Product
from app.modules.inventory.models.stock_balance import StockBalance
from app.modules.inventory.models.warehouse import Warehouse
from app.modules.manufacturing.models.production_order import ProductionOrder, ProductionScrap
from app.modules.organization.models.department import Department


class AggregationService:
    """Service generating high-performance aggregations and chart datasets."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_financial_trend(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        params: AnalyticsFilterParams,
    ) -> ChartDatasetResponse:
        """Returns monthly / period time-series of Revenue vs Expenses with Margin breakdown."""
        curr_start, curr_end, _, _, _ = KPIService.resolve_date_range(params)

        # Build bucket intervals (6-12 monthly buckets)
        buckets: list[TimeSeriesPoint] = []
        datetime.now(UTC)

        # Generate 6 intervals ending at curr_end
        interval_count = 6
        step_days = (
            max(1, (curr_end - curr_start).days // interval_count)
            if (curr_end - curr_start).days > 6
            else 1
        )

        for i in range(interval_count):
            b_start = curr_start + timedelta(days=i * step_days)
            b_end = curr_start + timedelta(days=(i + 1) * step_days)
            if b_end > curr_end:
                b_end = curr_end

            # Query revenue for bucket
            rev_q = select(func.coalesce(func.sum(Invoice.total_amount), 0)).where(
                Invoice.tenant_id == tenant_id,
                Invoice.organization_id == org_id,
                Invoice.status.in_(["SENT", "PAID", "POSTED", "PARTIALLY_PAID"]),
                Invoice.created_at >= b_start,
                Invoice.created_at <= b_end,
            )
            exp_q = select(func.coalesce(func.sum(Bill.total_amount), 0)).where(
                Bill.tenant_id == tenant_id,
                Bill.organization_id == org_id,
                Bill.status.in_(["APPROVED", "PAID", "POSTED", "PARTIALLY_PAID"]),
                Bill.created_at >= b_start,
                Bill.created_at <= b_end,
            )

            rev = Decimal(str((await self.session.scalar(rev_q)) or 0))
            exp = Decimal(str((await self.session.scalar(exp_q)) or 0))

            label = b_start.strftime("%b %d") if step_days <= 7 else b_start.strftime("%b %Y")
            buckets.append(
                TimeSeriesPoint(
                    timestamp=b_start.strftime("%Y-%m-%d"),
                    label=label,
                    primary_value=rev,
                    secondary_value=exp,
                    breakdown={
                        "revenue": rev,
                        "expenses": exp,
                        "net_profit": rev - exp,
                    },
                )
            )

        # Breakdown by Invoice Status / Customer
        breakdown_stmt = (
            select(
                Invoice.status,
                func.count(Invoice.id).label("count"),
                func.coalesce(func.sum(Invoice.total_amount), 0).label("total"),
            )
            .where(
                Invoice.tenant_id == tenant_id,
                Invoice.organization_id == org_id,
                Invoice.created_at >= curr_start,
                Invoice.created_at <= curr_end,
            )
            .group_by(Invoice.status)
        )
        breakdown_res = await self.session.execute(breakdown_stmt)
        breakdowns: list[DimensionalBucket] = []
        tot_all = sum([Decimal(str(r.total)) for r in breakdown_res.all()])
        breakdown_res = await self.session.execute(breakdown_stmt)

        for r in breakdown_res.all():
            amt = Decimal(str(r.total))
            pct = round((amt / tot_all) * Decimal("100.0"), 1) if tot_all > 0 else Decimal("0.0")
            breakdowns.append(
                DimensionalBucket(
                    dimension_key=r.status,
                    dimension_label=r.status.replace("_", " ").title(),
                    count=r.count,
                    total_amount=amt,
                    percentage_share=pct,
                )
            )

        return ChartDatasetResponse(
            title="Financial Performance & Profitability Trend",
            chart_type="LINE",
            series=buckets,
            breakdowns=breakdowns,
            summary_metrics={"total_buckets": len(buckets)},
        )

    async def get_sales_pipeline_distribution(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        params: AnalyticsFilterParams,
    ) -> ChartDatasetResponse:
        """Returns distribution of CRM Deals across pipeline stages."""
        curr_start, curr_end, _, _, _ = KPIService.resolve_date_range(params)

        stmt = (
            select(
                PipelineStage.name.label("stage_name"),
                func.count(Deal.id).label("count"),
                func.coalesce(func.sum(Deal.value), 0).label("total_val"),
            )
            .join(PipelineStage, Deal.stage_id == PipelineStage.id)
            .where(
                Deal.tenant_id == tenant_id,
                Deal.organization_id == org_id,
                Deal.created_at >= curr_start,
                Deal.created_at <= curr_end,
            )
            .group_by(PipelineStage.name)
        )
        res = await self.session.execute(stmt)
        rows = res.all()
        total_val = sum([Decimal(str(r.total_val)) for r in rows])

        breakdowns: list[DimensionalBucket] = []
        for r in rows:
            amt = Decimal(str(r.total_val))
            pct = (
                round((amt / total_val) * Decimal("100.0"), 1) if total_val > 0 else Decimal("0.0")
            )
            breakdowns.append(
                DimensionalBucket(
                    dimension_key=r.stage_name,
                    dimension_label=r.stage_name.replace("_", " ").title(),
                    count=r.count,
                    total_amount=amt,
                    percentage_share=pct,
                )
            )

        return ChartDatasetResponse(
            title="Sales Pipeline Funnel Distribution",
            chart_type="DONUT",
            series=[],
            breakdowns=breakdowns,
            summary_metrics={"total_pipeline_value": total_val},
        )

    async def get_inventory_warehouse_breakdown(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> ChartDatasetResponse:
        """Returns stock valuation grouped by Warehouse."""
        stmt = (
            select(
                Warehouse.name.label("wh_name"),
                func.count(StockBalance.id).label("sku_count"),
                func.coalesce(
                    func.sum(
                        StockBalance.quantity_on_hand * func.coalesce(Product.cost_price, 10.0)
                    ),
                    0,
                ).label("valuation"),
            )
            .select_from(Warehouse)
            .join(StockBalance, Warehouse.id == StockBalance.warehouse_id)
            .join(Product, StockBalance.product_id == Product.id)
            .where(
                Warehouse.tenant_id == tenant_id,
                Warehouse.organization_id == org_id,
            )
            .group_by(Warehouse.id, Warehouse.name)
        )
        res = await self.session.execute(stmt)
        rows = res.all()
        total_val = sum([Decimal(str(r.valuation)) for r in rows])

        breakdowns: list[DimensionalBucket] = []
        for r in rows:
            amt = Decimal(str(r.valuation))
            pct = (
                round((amt / total_val) * Decimal("100.0"), 1) if total_val > 0 else Decimal("0.0")
            )
            breakdowns.append(
                DimensionalBucket(
                    dimension_key=r.wh_name,
                    dimension_label=r.wh_name,
                    count=r.sku_count,
                    total_amount=amt,
                    percentage_share=pct,
                )
            )

        return ChartDatasetResponse(
            title="Inventory Valuation by Warehouse",
            chart_type="BAR",
            series=[],
            breakdowns=breakdowns,
            summary_metrics={"total_valuation": total_val},
        )

    async def get_manufacturing_output_trend(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        params: AnalyticsFilterParams,
    ) -> ChartDatasetResponse:
        """Returns manufacturing output and scrap metrics time-series."""
        curr_start, curr_end, _, _, _ = KPIService.resolve_date_range(params)

        interval_count = 6
        step_days = (
            max(1, (curr_end - curr_start).days // interval_count)
            if (curr_end - curr_start).days > 6
            else 1
        )
        buckets: list[TimeSeriesPoint] = []

        for i in range(interval_count):
            b_start = curr_start + timedelta(days=i * step_days)
            b_end = curr_start + timedelta(days=(i + 1) * step_days)
            if b_end > curr_end:
                b_end = curr_end

            prod_q = select(func.coalesce(func.sum(ProductionOrder.produced_quantity), 0)).where(
                ProductionOrder.tenant_id == tenant_id,
                ProductionOrder.organization_id == org_id,
                ProductionOrder.created_at >= b_start,
                ProductionOrder.created_at <= b_end,
            )
            scrap_q = select(func.coalesce(func.sum(ProductionScrap.scrap_quantity), 0)).where(
                ProductionScrap.tenant_id == tenant_id,
                ProductionScrap.organization_id == org_id,
                ProductionScrap.recorded_at >= b_start,
                ProductionScrap.recorded_at <= b_end,
            )

            prod = Decimal(str((await self.session.scalar(prod_q)) or 0))
            scrap = Decimal(str((await self.session.scalar(scrap_q)) or 0))

            label = b_start.strftime("%b %d") if step_days <= 7 else b_start.strftime("%b %Y")
            buckets.append(
                TimeSeriesPoint(
                    timestamp=b_start.strftime("%Y-%m-%d"),
                    label=label,
                    primary_value=prod,
                    secondary_value=scrap,
                    breakdown={"produced": prod, "scrapped": scrap},
                )
            )

        return ChartDatasetResponse(
            title="Manufacturing Volume & Scrap Trend",
            chart_type="AREA",
            series=buckets,
            breakdowns=[],
        )

    async def get_hr_department_headcount(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> ChartDatasetResponse:
        """Returns active employee headcount distributed by Department."""
        stmt = (
            select(
                Department.name.label("dept_name"),
                func.count(Employee.id).label("headcount"),
            )
            .select_from(Department)
            .join(Employee, Department.id == Employee.department_id)
            .where(
                Department.tenant_id == tenant_id,
                Department.organization_id == org_id,
                Employee.employment_status.in_(["ACTIVE", "PROBATION"]),
            )
            .group_by(Department.id, Department.name)
        )
        res = await self.session.execute(stmt)
        rows = res.all()
        total_hc = sum([r.headcount for r in rows])

        breakdowns: list[DimensionalBucket] = []
        for r in rows:
            pct = (
                round((Decimal(str(r.headcount)) / Decimal(str(total_hc))) * Decimal("100.0"), 1)
                if total_hc > 0
                else Decimal("0.0")
            )
            breakdowns.append(
                DimensionalBucket(
                    dimension_key=r.dept_name,
                    dimension_label=r.dept_name,
                    count=r.headcount,
                    total_amount=Decimal(str(r.headcount)),
                    percentage_share=pct,
                )
            )

        return ChartDatasetResponse(
            title="Headcount Distribution by Department",
            chart_type="DONUT",
            series=[],
            breakdowns=breakdowns,
            summary_metrics={"total_headcount": total_hc},
        )
