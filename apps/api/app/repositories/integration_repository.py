import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.integration import (
    APIKey,
    Connector,
    ConnectorConfig,
    ConnectorLog,
    EventLog,
    EventTopic,
    IntegrationAudit,
    MessageQueueLog,
    Webhook,
    WebhookEvent,
)


class IntegrationRepository:
    """Async SQLAlchemy repository for Enterprise Integration Platform operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ----------------------------------------------------
    # Connector Operations
    # ----------------------------------------------------
    async def get_connector_by_id(self, connector_id: uuid.UUID) -> Connector | None:
        result = await self.db.execute(
            select(Connector).where(Connector.id == connector_id)
        )
        return result.scalar_one_or_none()

    async def get_connector_by_slug(
        self, slug: str, org_id: uuid.UUID | None = None
    ) -> Connector | None:
        stmt = select(Connector).where(Connector.slug == slug)
        if org_id:
            stmt = stmt.where(
                (Connector.organization_id == org_id)
                | (Connector.organization_id.is_(None))
            )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_connectors(
        self,
        org_id: uuid.UUID | None = None,
        category: str | None = None,
        provider: str | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Connector]:
        stmt = select(Connector)
        if org_id:
            stmt = stmt.where(
                (Connector.organization_id == org_id)
                | (Connector.organization_id.is_(None))
            )
        if category:
            stmt = stmt.where(Connector.category == category)
        if provider:
            stmt = stmt.where(Connector.provider == provider)
        if status:
            stmt = stmt.where(Connector.status == status)
        stmt = stmt.offset(skip).limit(limit).order_by(Connector.name.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_connector(self, connector: Connector) -> Connector:
        self.db.add(connector)
        await self.db.commit()
        await self.db.refresh(connector)
        return connector

    async def create_connector_config(self, config: ConnectorConfig) -> ConnectorConfig:
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def get_connector_config(
        self, config_id: uuid.UUID, org_id: uuid.UUID | None = None
    ) -> ConnectorConfig | None:
        stmt = select(ConnectorConfig).where(ConnectorConfig.id == config_id)
        if org_id:
            stmt = stmt.where(ConnectorConfig.organization_id == org_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_connector_configs(
        self, org_id: uuid.UUID | None = None
    ) -> list[ConnectorConfig]:
        stmt = select(ConnectorConfig)
        if org_id:
            stmt = stmt.where(ConnectorConfig.organization_id == org_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_connector_log(self, log: ConnectorLog) -> ConnectorLog:
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def list_connector_logs(
        self, connector_id: uuid.UUID, limit: int = 50
    ) -> list[ConnectorLog]:
        stmt = (
            select(ConnectorLog)
            .where(ConnectorLog.connector_id == connector_id)
            .order_by(ConnectorLog.executed_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ----------------------------------------------------
    # Webhook Operations
    # ----------------------------------------------------
    async def create_webhook(self, webhook: Webhook) -> Webhook:
        self.db.add(webhook)
        await self.db.commit()
        await self.db.refresh(webhook)
        return webhook

    async def get_webhook_by_id(
        self, webhook_id: uuid.UUID, org_id: uuid.UUID | None = None
    ) -> Webhook | None:
        stmt = select(Webhook).where(Webhook.id == webhook_id)
        if org_id:
            stmt = stmt.where(Webhook.organization_id == org_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_webhooks(self, org_id: uuid.UUID | None = None) -> list[Webhook]:
        stmt = select(Webhook)
        if org_id:
            stmt = stmt.where(Webhook.organization_id == org_id)
        result = await self.db.execute(stmt.order_by(Webhook.created_at.desc()))
        return list(result.scalars().all())

    async def create_webhook_event(self, event: WebhookEvent) -> WebhookEvent:
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def list_webhook_events(
        self, webhook_id: uuid.UUID, limit: int = 50
    ) -> list[WebhookEvent]:
        stmt = (
            select(WebhookEvent)
            .where(WebhookEvent.webhook_id == webhook_id)
            .order_by(WebhookEvent.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ----------------------------------------------------
    # API Key & Security Operations
    # ----------------------------------------------------
    async def create_api_key(self, api_key: APIKey) -> APIKey:
        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
        return api_key

    async def get_api_key_by_hash(self, hashed_key: str) -> APIKey | None:
        stmt = select(APIKey).where(APIKey.hashed_key == hashed_key)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_api_keys(self, org_id: uuid.UUID | None = None) -> list[APIKey]:
        stmt = select(APIKey)
        if org_id:
            stmt = stmt.where(APIKey.organization_id == org_id)
        result = await self.db.execute(stmt.order_by(APIKey.created_at.desc()))
        return list(result.scalars().all())

    # ----------------------------------------------------
    # Event Bus Operations
    # ----------------------------------------------------
    async def create_event_topic(self, topic: EventTopic) -> EventTopic:
        self.db.add(topic)
        await self.db.commit()
        await self.db.refresh(topic)
        return topic

    async def get_topic_by_name(self, name: str) -> EventTopic | None:
        stmt = select(EventTopic).where(EventTopic.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_event_topics(
        self, org_id: uuid.UUID | None = None
    ) -> list[EventTopic]:
        stmt = select(EventTopic)
        if org_id:
            stmt = stmt.where(
                (EventTopic.organization_id == org_id)
                | (EventTopic.organization_id.is_(None))
            )
        result = await self.db.execute(stmt.order_by(EventTopic.name.asc()))
        return list(result.scalars().all())

    async def create_event_log(self, event_log: EventLog) -> EventLog:
        self.db.add(event_log)
        await self.db.commit()
        await self.db.refresh(event_log)
        return event_log

    async def list_event_logs(
        self,
        topic_name: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[EventLog]:
        stmt = select(EventLog)
        if topic_name:
            stmt = stmt.where(EventLog.topic_name == topic_name)
        if status:
            stmt = stmt.where(EventLog.status == status)
        stmt = stmt.order_by(EventLog.published_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ----------------------------------------------------
    # Message Queue Operations
    # ----------------------------------------------------
    async def create_queue_log(self, log: MessageQueueLog) -> MessageQueueLog:
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def list_queue_logs(
        self,
        queue_name: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[MessageQueueLog]:
        stmt = select(MessageQueueLog)
        if queue_name:
            stmt = stmt.where(MessageQueueLog.queue_name == queue_name)
        if status:
            stmt = stmt.where(MessageQueueLog.status == status)
        stmt = stmt.order_by(MessageQueueLog.created_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ----------------------------------------------------
    # Integration Audit Operations
    # ----------------------------------------------------
    async def log_audit(self, audit: IntegrationAudit) -> IntegrationAudit:
        self.db.add(audit)
        await self.db.commit()
        await self.db.refresh(audit)
        return audit

    async def list_audit_logs(
        self, org_id: uuid.UUID | None = None, limit: int = 100
    ) -> list[IntegrationAudit]:
        stmt = select(IntegrationAudit)
        if org_id:
            stmt = stmt.where(IntegrationAudit.organization_id == org_id)
        stmt = stmt.order_by(IntegrationAudit.timestamp.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
