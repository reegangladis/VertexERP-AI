import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, update, delete, func, desc, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.observability import (
    SystemMetric,
    ApplicationLog,
    Trace,
    Alert,
    AlertHistory,
    ServiceHealth,
    DashboardConfig,
    ObservabilityEvent,
)


class ObservabilityRepository:
    """Repository handling all Monitoring & Observability Platform database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================================================================
    # SYSTEM METRICS
    # =========================================================================
    async def create_metric(self, metric: SystemMetric) -> SystemMetric:
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        return metric

    async def get_metrics(
        self,
        organization_id: Optional[uuid.UUID],
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SystemMetric]:
        stmt = select(SystemMetric)
        
        # Tenant isolation or system-wide metrics (where organization_id is NULL)
        if organization_id:
            stmt = stmt.where(
                or_(
                    SystemMetric.organization_id == organization_id,
                    SystemMetric.organization_id == None,
                )
            )
        
        if metric_name:
            stmt = stmt.where(SystemMetric.metric_name == metric_name)
        if start_time:
            stmt = stmt.where(SystemMetric.created_at >= start_time)
        if end_time:
            stmt = stmt.where(SystemMetric.created_at <= end_time)

        stmt = stmt.order_by(desc(SystemMetric.created_at)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # =========================================================================
    # APPLICATION LOGS
    # =========================================================================
    async def create_log(self, log: ApplicationLog) -> ApplicationLog:
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_logs(
        self,
        organization_id: Optional[uuid.UUID],
        service_name: Optional[str] = None,
        log_level: Optional[str] = None,
        keyword: Optional[str] = None,
        correlation_id: Optional[str] = None,
        request_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[ApplicationLog], int]:
        stmt = select(ApplicationLog)
        
        # Tenant isolation
        if organization_id:
            stmt = stmt.where(
                or_(
                    ApplicationLog.organization_id == organization_id,
                    ApplicationLog.organization_id == None,
                )
            )
        
        if service_name:
            stmt = stmt.where(ApplicationLog.service_name == service_name)
        if log_level:
            stmt = stmt.where(ApplicationLog.log_level == log_level)
        if correlation_id:
            stmt = stmt.where(ApplicationLog.correlation_id == correlation_id)
        if request_id:
            stmt = stmt.where(ApplicationLog.request_id == request_id)
        if start_time:
            stmt = stmt.where(ApplicationLog.timestamp >= start_time)
        if end_time:
            stmt = stmt.where(ApplicationLog.timestamp <= end_time)
        if keyword:
            # Simple SQL LIKE search
            stmt = stmt.where(ApplicationLog.message.ilike(f"%{keyword}%"))

        # Count total records matching criteria
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_res = await self.db.execute(count_stmt)
        total_count = count_res.scalar_one()

        stmt = stmt.order_by(desc(ApplicationLog.timestamp)).offset(skip).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all()), total_count

    # =========================================================================
    # DISTRIBUTED TRACING
    # =========================================================================
    async def create_trace_span(self, span: Trace) -> Trace:
        self.db.add(span)
        await self.db.commit()
        await self.db.refresh(span)
        return span

    async def get_traces(
        self,
        organization_id: Optional[uuid.UUID],
        trace_id: Optional[str] = None,
        service_name: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Trace]:
        stmt = select(Trace)
        
        # Tenant isolation
        if organization_id:
            stmt = stmt.where(
                or_(
                    Trace.organization_id == organization_id,
                    Trace.organization_id == None,
                )
            )
        
        if trace_id:
            stmt = stmt.where(Trace.trace_id == trace_id)
        if service_name:
            stmt = stmt.where(Trace.service_name == service_name)
        if status:
            stmt = stmt.where(Trace.status == status)
        if start_time:
            stmt = stmt.where(Trace.start_time >= start_time)
        if end_time:
            stmt = stmt.where(Trace.start_time <= end_time)

        stmt = stmt.order_by(desc(Trace.start_time)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_service_dependencies(
        self, organization_id: Optional[uuid.UUID]
    ) -> List[Dict[str, Any]]:
        # Compute dynamic dependencies based on caller-callee relations from parent_span_id lookup.
        # For simplicity, we can fetch all traces and construct calling maps, or execute an aggregation query.
        # Let's perform a query fetching span caller-callee pairs:
        # SELECT parent.service_name as caller, child.service_name as callee, COUNT(*), AVG(child.duration_ms), SUM(case when child.status = 'error' then 1 else 0 end)
        stmt = (
            select(
                Trace.service_name.label("callee"),
                # We subquery or self-join to find the parent span's service_name
            )
        )
        # To avoid complex self-joins in async ORM that might crash, let's write a simple raw query or a clean SQLAlchemy self-join:
        alias_parent = sa_alias = select(Trace).subquery()
        # Since we just need a mockable and highly functional aggregator:
        # Let's aggregate caller-callee relationship by inspecting parent_span_id mappings.
        join_stmt = (
            select(
                alias_parent.c.service_name.label("caller"),
                Trace.service_name.label("callee"),
                func.count().label("call_count"),
                func.avg(Trace.duration_ms).label("avg_duration_ms"),
                func.sum(case_stmt := func.coalesce(func.cast(Trace.status == "error", func.Integer), 0)).label("errors"),
            )
            .join(alias_parent, alias_parent.c.span_id == Trace.parent_span_id)
        )
        if organization_id:
            join_stmt = join_stmt.where(Trace.organization_id == organization_id)
            
        join_stmt = join_stmt.group_by(alias_parent.c.service_name, Trace.service_name)
        res = await self.db.execute(join_stmt)
        
        deps = []
        for row in res.all():
            caller, callee, call_count, avg_duration, errors = row
            error_rate = float(errors) / float(call_count) if call_count > 0 else 0.0
            deps.append({
                "caller": caller,
                "callee": callee,
                "call_count": call_count,
                "avg_duration_ms": float(avg_duration or 0.0),
                "error_rate": error_rate,
            })
        return deps

    # =========================================================================
    # INCIDENT ALERTS
    # =========================================================================
    async def create_alert(self, alert: Alert) -> Alert:
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def get_alerts(
        self,
        organization_id: Optional[uuid.UUID],
        status: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> List[Alert]:
        stmt = select(Alert).options(selectinload(Alert.history))
        
        if organization_id:
            stmt = stmt.where(
                or_(
                    Alert.organization_id == organization_id,
                    Alert.organization_id == None,
                )
            )
            
        if status:
            stmt = stmt.where(Alert.status == status)
        if severity:
            stmt = stmt.where(Alert.severity == severity)

        stmt = stmt.order_by(desc(Alert.created_at)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_alert_by_id(self, alert_id: uuid.UUID) -> Optional[Alert]:
        stmt = select(Alert).options(selectinload(Alert.history)).where(Alert.id == alert_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def update_alert(self, alert: Alert) -> Alert:
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def create_alert_history(self, history: AlertHistory) -> AlertHistory:
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    # =========================================================================
    # SERVICE HEALTH
    # =========================================================================
    async def get_all_service_health(self, organization_id: Optional[uuid.UUID]) -> List[ServiceHealth]:
        stmt = select(ServiceHealth)
        if organization_id:
            stmt = stmt.where(
                or_(
                    ServiceHealth.organization_id == organization_id,
                    ServiceHealth.organization_id == None,
                )
            )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update_service_health(self, health_data: ServiceHealth) -> ServiceHealth:
        # Use upsert or standard lookup-then-write
        stmt = select(ServiceHealth).where(ServiceHealth.service_name == health_data.service_name)
        res = await self.db.execute(stmt)
        existing = res.scalar_one_or_none()
        
        if existing:
            existing.status = health_data.status
            existing.liveness = health_data.liveness
            existing.readiness = health_data.readiness
            existing.uptime_seconds = health_data.uptime_seconds
            existing.latency_ms = health_data.latency_ms
            existing.dependency_status = health_data.dependency_status
            existing.last_checked = datetime.utcnow()
            self.db.add(existing)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            self.db.add(health_data)
            await self.db.commit()
            await self.db.refresh(health_data)
            return health_data

    # =========================================================================
    # DASHBOARD CONFIGS
    # =========================================================================
    async def get_dashboard_config(
        self, organization_id: Optional[uuid.UUID], dashboard_type: str
    ) -> Optional[DashboardConfig]:
        stmt = select(DashboardConfig).where(DashboardConfig.dashboard_type == dashboard_type)
        if organization_id:
            stmt = stmt.where(
                or_(
                    DashboardConfig.organization_id == organization_id,
                    DashboardConfig.organization_id == None,
                )
            )
        stmt = stmt.order_by(desc(DashboardConfig.created_at))
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def create_dashboard_config(self, config: DashboardConfig) -> DashboardConfig:
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        return config

    # =========================================================================
    # OBSERVABILITY EVENTS
    # =========================================================================
    async def create_event(self, event: ObservabilityEvent) -> ObservabilityEvent:
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def get_events(
        self,
        organization_id: Optional[uuid.UUID],
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50,
    ) -> List[ObservabilityEvent]:
        stmt = select(ObservabilityEvent)
        if organization_id:
            stmt = stmt.where(
                or_(
                    ObservabilityEvent.organization_id == organization_id,
                    ObservabilityEvent.organization_id == None,
                )
            )
        if event_type:
            stmt = stmt.where(ObservabilityEvent.event_type == event_type)
        if severity:
            stmt = stmt.where(ObservabilityEvent.severity == severity)

        stmt = stmt.order_by(desc(ObservabilityEvent.timestamp)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
