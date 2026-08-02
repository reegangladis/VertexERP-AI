import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ----------------------------------------------------
# Connector Schemas
# ----------------------------------------------------
class ConnectorBase(BaseModel):
    name: str = Field(..., max_length=150)
    slug: str = Field(..., max_length=100)
    category: str = Field(
        ..., description="erp, crm, payment, storage, email, sms, messaging, ai, idp"
    )
    version: str = Field(default="1.0.0")
    description: str | None = None
    provider: str = Field(
        ...,
        description="sap, salesforce, stripe, aws, twilio, slack, openai, auth0, etc.",
    )
    auth_type: str = Field(
        default="oauth2", description="oauth2, api_key, basic, jwt, custom"
    )
    status: str = Field(default="active")
    icon_url: str | None = None
    schema_definition: dict[str, Any] | None = None
    supported_actions: list[str] | None = None
    is_custom: bool = False


class ConnectorCreate(ConnectorBase):
    organization_id: uuid.UUID | None = None


class ConnectorUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    version: str | None = None
    description: str | None = None
    provider: str | None = None
    auth_type: str | None = None
    status: str | None = None
    icon_url: str | None = None
    schema_definition: dict[str, Any] | None = None
    supported_actions: list[str] | None = None


class ConnectorOut(ConnectorBase):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConnectorConfigCreate(BaseModel):
    connector_id: uuid.UUID
    name: str
    credentials: dict[str, Any] = Field(
        ..., description="Raw secret credentials dict (will be encrypted)"
    )
    endpoint_url: str | None = None
    environment: str = "production"
    settings: dict[str, Any] | None = None


class ConnectorConfigUpdate(BaseModel):
    name: str | None = None
    credentials: dict[str, Any] | None = None
    endpoint_url: str | None = None
    environment: str | None = None
    settings: dict[str, Any] | None = None
    is_enabled: bool | None = None


class ConnectorConfigOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    connector_id: uuid.UUID
    name: str
    endpoint_url: str | None = None
    environment: str
    settings: dict[str, Any] | None = None
    is_enabled: bool
    last_connected_at: datetime | None = None
    health_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConnectorLogOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    connector_id: uuid.UUID
    action: str
    status: str
    latency_ms: float
    request_snippet: dict[str, Any] | None = None
    response_snippet: dict[str, Any] | None = None
    error_message: str | None = None
    records_processed: int
    executed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConnectorExecuteRequest(BaseModel):
    config_id: uuid.UUID
    action: str
    payload: dict[str, Any] = Field(default_factory=dict)


class ConnectorExecuteResponse(BaseModel):
    status: str
    action: str
    records_affected: int = 0
    latency_ms: float
    data: dict[str, Any] | None = None
    error: str | None = None


# ----------------------------------------------------
# Webhook Schemas
# ----------------------------------------------------
class WebhookBase(BaseModel):
    name: str = Field(..., max_length=150)
    target_url: str = Field(..., description="Destination webhook URL")
    events: list[str] = Field(
        ..., description="Subscribed event list e.g. ['order.created']"
    )
    signature_header: str = "X-Webhook-Signature"
    is_active: bool = True
    retry_limit: int = 5
    timeout_seconds: int = 30
    headers: dict[str, str] | None = None
    description: str | None = None


class WebhookCreate(WebhookBase):
    secret_key: str | None = None  # Generated automatically if omitted


class WebhookUpdate(BaseModel):
    name: str | None = None
    target_url: str | None = None
    events: list[str] | None = None
    is_active: bool | None = None
    retry_limit: int | None = None
    timeout_seconds: int | None = None
    headers: dict[str, str] | None = None
    description: str | None = None


class WebhookOut(WebhookBase):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    secret_key: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebhookEventOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    webhook_id: uuid.UUID
    event_type: str
    payload: dict[str, Any]
    status: str
    http_status: int | None = None
    attempt_count: int
    max_attempts: int
    latency_ms: float
    response_body: str | None = None
    error_log: str | None = None
    next_retry_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebhookDispatchTest(BaseModel):
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)


# ----------------------------------------------------
# API Key & Gateway Auth Schemas
# ----------------------------------------------------
class APIKeyCreate(BaseModel):
    name: str = Field(..., max_length=150)
    scopes: list[str] = Field(default_factory=lambda: ["read", "write"])
    rate_limit_rps: int = 50
    rate_limit_rpm: int = 1000
    expires_in_days: int | None = 365


class APIKeyOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    name: str
    key_prefix: str
    raw_key: str | None = Field(None, description="Only populated on creation")
    scopes: list[str]
    rate_limit_rps: int
    rate_limit_rpm: int
    status: str
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class APIKeyVerifyRequest(BaseModel):
    api_key: str


class APIKeyVerifyResponse(BaseModel):
    valid: bool
    key_id: str | None = None
    organization_id: str | None = None
    scopes: list[str] = Field(default_factory=list)
    rate_limit_rps: int = 50


# ----------------------------------------------------
# Event Bus Schemas
# ----------------------------------------------------
class EventTopicCreate(BaseModel):
    name: str = Field(..., max_length=150)
    description: str | None = None
    topic_schema: dict[str, Any] | None = None
    retention_hours: int = 168
    consumer_groups: list[str] | None = Field(default_factory=lambda: ["default"])


class EventTopicOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    name: str
    description: str | None = None
    topic_schema: dict[str, Any] | None = None
    retention_hours: int
    consumer_groups: list[str] | None = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventPublishRequest(BaseModel):
    topic_name: str
    event_id: str | None = None
    payload: dict[str, Any]
    headers: dict[str, Any] | None = None
    partition_key: str | None = None


class EventLogOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    topic_id: uuid.UUID
    topic_name: str
    event_id: str
    payload: dict[str, Any]
    headers: dict[str, Any] | None = None
    status: str
    partition_key: str | None = None
    is_replayed: bool
    published_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventReplayRequest(BaseModel):
    topic_name: str
    from_timestamp: datetime | None = None
    to_timestamp: datetime | None = None
    limit: int = 100


# ----------------------------------------------------
# Message Queue Schemas
# ----------------------------------------------------
class QueueMessagePublish(BaseModel):
    queue_name: str
    message_id: str | None = None
    payload: dict[str, Any]
    max_retries: int = 3


class QueueMessageOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    queue_name: str
    message_id: str
    payload: dict[str, Any]
    status: str
    attempt_count: int
    max_retries: int
    consumer_id: str | None = None
    error_details: str | None = None
    processed_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------------------------------------------
# API Gateway & Analytics Schemas
# ----------------------------------------------------
class GatewayRoutePolicy(BaseModel):
    route_path: str
    target_service: str
    version: str = "v1"
    rate_limit_rps: int = 100
    cache_ttl_seconds: int = 0
    auth_required: bool = True
    allowed_methods: list[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE"]
    )


class GatewayAnalyticsSummary(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    rate_limited_requests: int
    avg_latency_ms: float
    p95_latency_ms: float
    cache_hit_ratio: float
    active_connectors: int
    active_webhooks: int
    queue_depth: int
