import uuid
from datetime import datetime, date
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, update, delete, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
from app.repositories.base import BaseRepository


class AnalyticsRepository(BaseRepository[AnalyticsDashboard]):
    """SQLAlchemy 2.0 Async Repository for Analytics & BI platform."""

    def __init__(self, session: AsyncSession):
        super().__init__(AnalyticsDashboard, session)
        self.session = session

    # --- Dashboards & Widgets ---

    async def get_dashboards(
        self, organization_id: uuid.UUID, scope: Optional[str] = None
    ) -> List[AnalyticsDashboard]:
        query = select(AnalyticsDashboard).options(selectinload(AnalyticsDashboard.widgets)).where(
            AnalyticsDashboard.organization_id == organization_id,
            AnalyticsDashboard.deleted_at.is_(None),
        )
        if scope:
            query = query.where(AnalyticsDashboard.scope == scope)
        query = query.order_by(AnalyticsDashboard.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_dashboard_by_id(
        self, dashboard_id: uuid.UUID, organization_id: uuid.UUID
    ) -> Optional[AnalyticsDashboard]:
        query = select(AnalyticsDashboard).options(selectinload(AnalyticsDashboard.widgets)).where(
            AnalyticsDashboard.id == dashboard_id,
            AnalyticsDashboard.organization_id == organization_id,
            AnalyticsDashboard.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_widget(self, widget: AnalyticsWidget) -> AnalyticsWidget:
        self.session.add(widget)
        await self.session.commit()
        await self.session.refresh(widget)
        return widget

    async def get_widget_by_id(self, widget_id: uuid.UUID, organization_id: uuid.UUID) -> Optional[AnalyticsWidget]:
        query = select(AnalyticsWidget).where(
            AnalyticsWidget.id == widget_id,
            AnalyticsWidget.organization_id == organization_id,
            AnalyticsWidget.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    # --- KPIs & KPI Values ---

    async def get_kpis(
        self, organization_id: uuid.UUID, category: Optional[str] = None, scope: Optional[str] = None
    ) -> List[KPI]:
        query = select(KPI).options(selectinload(KPI.values)).where(
            KPI.organization_id == organization_id,
            KPI.deleted_at.is_(None),
        )
        if category:
            query = query.where(KPI.category == category)
        if scope:
            query = query.where(KPI.scope == scope)
        query = query.order_by(KPI.name.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_kpi_by_id(self, kpi_id: uuid.UUID, organization_id: uuid.UUID) -> Optional[KPI]:
        query = select(KPI).options(selectinload(KPI.values)).where(
            KPI.id == kpi_id,
            KPI.organization_id == organization_id,
            KPI.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_kpi(self, kpi: KPI) -> KPI:
        self.session.add(kpi)
        await self.session.commit()
        await self.session.refresh(kpi)
        return kpi

    async def add_kpi_value(self, kpi_value: KPIValue) -> KPIValue:
        self.session.add(kpi_value)
        await self.session.commit()
        await self.session.refresh(kpi_value)
        return kpi_value

    async def get_kpi_values(self, kpi_id: uuid.UUID, limit: int = 12) -> List[KPIValue]:
        query = select(KPIValue).where(
            KPIValue.kpi_id == kpi_id,
            KPIValue.deleted_at.is_(None),
        ).order_by(KPIValue.period_start.asc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # --- Reports & Saved Reports & Templates ---

    async def get_reports(
        self, organization_id: uuid.UUID, category: Optional[str] = None
    ) -> List[Report]:
        query = select(Report).where(
            Report.organization_id == organization_id,
            Report.deleted_at.is_(None),
        )
        if category:
            query = query.where(Report.report_category == category)
        query = query.order_by(Report.name.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_report_by_id(self, report_id: uuid.UUID, organization_id: uuid.UUID) -> Optional[Report]:
        query = select(Report).where(
            Report.id == report_id,
            Report.organization_id == organization_id,
            Report.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_report(self, report: Report) -> Report:
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get_saved_reports(self, organization_id: uuid.UUID, user_id: uuid.UUID) -> List[SavedReport]:
        query = select(SavedReport).options(selectinload(SavedReport.report)).where(
            SavedReport.organization_id == organization_id,
            SavedReport.user_id == user_id,
            SavedReport.deleted_at.is_(None),
        ).order_by(SavedReport.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_saved_report(self, saved_report: SavedReport) -> SavedReport:
        self.session.add(saved_report)
        await self.session.commit()
        await self.session.refresh(saved_report)
        return saved_report

    async def get_report_templates(self, organization_id: Optional[uuid.UUID] = None) -> List[ReportTemplate]:
        query = select(ReportTemplate).where(
            or_(
                ReportTemplate.organization_id == organization_id,
                ReportTemplate.is_system.is_(True),
            ),
            ReportTemplate.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_report_template(self, template: ReportTemplate) -> ReportTemplate:
        self.session.add(template)
        await self.session.commit()
        await self.session.refresh(template)
        return template

    # --- Unified Global Search ---

    async def search_analytics(
        self, organization_id: uuid.UUID, query_str: str
    ) -> Tuple[List[AnalyticsDashboard], List[Report], List[KPI], List[SavedReport]]:
        pattern = f"%{query_str}%"

        dashboards_q = select(AnalyticsDashboard).where(
            AnalyticsDashboard.organization_id == organization_id,
            AnalyticsDashboard.deleted_at.is_(None),
            or_(AnalyticsDashboard.title.ilike(pattern), AnalyticsDashboard.description.ilike(pattern)),
        ).limit(10)

        reports_q = select(Report).where(
            Report.organization_id == organization_id,
            Report.deleted_at.is_(None),
            or_(Report.name.ilike(pattern), Report.description.ilike(pattern)),
        ).limit(10)

        kpis_q = select(KPI).options(selectinload(KPI.values)).where(
            KPI.organization_id == organization_id,
            KPI.deleted_at.is_(None),
            or_(KPI.name.ilike(pattern), KPI.code.ilike(pattern)),
        ).limit(10)

        saved_reports_q = select(SavedReport).options(selectinload(SavedReport.report)).where(
            SavedReport.organization_id == organization_id,
            SavedReport.deleted_at.is_(None),
            SavedReport.title.ilike(pattern),
        ).limit(10)

        dashboards_res = await self.session.execute(dashboards_q)
        reports_res = await self.session.execute(reports_q)
        kpis_res = await self.session.execute(kpis_q)
        saved_res = await self.session.execute(saved_reports_q)

        return (
            list(dashboards_res.scalars().all()),
            list(reports_res.scalars().all()),
            list(kpis_res.scalars().all()),
            list(saved_res.scalars().all()),
        )
