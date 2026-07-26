import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


# ----------------------------------------------------
# Connector Schemas
# ----------------------------------------------------
class ConnectorBase(BaseModel):
    name: str = Field(..., max_length=150)
    slug: str = Field(..., max_length=100)
    category: str = Field(..., description="erp, crm, payment, storage, email, sms, messaging, ai, idp")
    version: str = Field(default="1.0.0")
    description: Optional[str] = None
    provider: str = Field(..., description="sap, salesforce, stripe, aws, twilio, slack, openai, auth0, etc.")
    auth_type: str = Field(default="oauth2", description="oauth2, api_key, basic, jwt, custom")
    status: str = Field(default="active")
    icon_url: Optional[str] = None
    schema_definition: Optional[Dict[str, Any]] = None
    supported_actions: Optional[List[str]] = None
    is_custom: bool = False


class ConnectorCreate(ConnectorBase):
    organization_id: Optional[uuid.UUID] = None


class ConnectorUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    provider: Optional[str] = None
    auth_type: Optional[str] = None
    status: Optional[str] = None
    icon_url: Optional[str] = None
    schema_definition: Optional[Dict[str, Any]] = None
    supported_actions: Optional[List[str]] = None


class ConnectorOut(ConnectorBase):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConnectorConfigCreate(BaseModel):
    connector_id: uuid.UUID
    name: str
    credentials: Dict[str, Any] = Field(..., description="Raw secret credentials dict (will be encrypted)")
    endpoint_url: Optional[str] = None
    environment: str = "production"
    settings: Optional[Dict[str, Any]] = None


class ConnectorConfigUpdate(BaseModel):
    name: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    endpoint_url: Optional[str] = None
    environment: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None


class ConnectorConfigOut(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    connector_id: uuid.UUID
    name: str
    endpoint_url: Optional[str] = None
    environment: str
    settings: Optional[Dict[str, Any]] = None
    is_enabled: bool
    last_connected_at: Optional[datetime] = None
    health_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConnectorLogOut(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    connector_id: uuid.UUID
    action: str
    status: str
    latency_ms: float
    request_snippet: Optional[Dict[str, Any]] = None
    response_snippet: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    records_processed: int
    executed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConnectorExecuteRequest(BaseModel):
    config_id: uuid.UUID
    action: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class ConnectorExecuteResponse(BaseModel):
    status: str
    action: str
    records_affected: int = 0
    latency_ms: float
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ----------------------------------------------------
# Webhook Schemas
# ----------------------------------------------------
class WebhookBase(BaseModel):
    name: str = Field(..., max_length=150)
    target_url: str = Field(..., description="Destination webhook URL")
    events: List[str] = Field(..., description="Subscribed event list e.g. ['order.created']")
    signature_header: str = "X-Webhook-Signature"
    is_active: bool = True
    retry_limit: int = 5
    timeout_seconds: int = 30
    headers: Optional[Dict[str, str]] = None
    description: Optional[str] = None


class WebhookCreate(WebhookBase):
    secret_key: Optional[str] = None  # Generated automatically if omitted


class WebhookUpdate(BaseModel):
    name: Optional[str] = None
    target_url: Optional[str] = None
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None
    retry_limit: Optional[int] = None
    timeout_seconds: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    description: Optional[str] = None


class WebhookOut(WebhookBase):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    secret_key: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebhookEventOut(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    webhook_id: uuid.UUID
    event_type: str
    payload: Dict[str, Any]
    status: str
    http_status: Optional[int] = None
    attempt_count: int
    max_attempts: int
    latency_ms: float
    response_body: Optional[str] = None
    error_log: Optional[str] = None
    next_retry_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebhookDispatchTest(BaseModel):
    event_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)


# ----------------------------------------------------
# API Key & Gateway Auth Schemas
# ----------------------------------------------------
class APIKeyCreate(BaseModel):
    name: str = Field(..., max_length=150)
    scopes: List[str] = Field(default_factory=lambda: ["read", "write"])
    rate_limit_rps: int = 50
    rate_limit_rpm: int = 1000
    expires_in_days: Optional[int] = 365


class APIKeyOut(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    name: str
    key_prefix: str
    raw_key: Optional[str] = Field(None, description="Only populated on creation")
    scopes: List[str]
    rate_limit_rps: int
    rate_limit_rpm: int
    status: str
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class APIKeyVerifyRequest(BaseModel):
    api_key: str


class APIKeyVerifyResponse(BaseModel):
    valid: bool
    key_id: Optional[str] = None
    organization_id: Optional[str] = None
    scopes: List[str] = Field(default_factory=list)
    rate_limit_rps: int = 50


# ----------------------------------------------------
# Event Bus Schemas
# ----------------------------------------------------
class EventTopicCreate(BaseModel):
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    topic_schema: Optional[Dict[str, Any]] = None
    retention_hours: int = 168
    consumer_groups: Optional[List[str]] = Field(default_factory=lambda: ["default"])


class EventTopicOut(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    name: str
    description: Optional[str] = None
    topic_schema: Optional[Dict[str, Any]] = None
    retention_hours: int
    consumer_groups: Optional[List[str]] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventPublishRequest(BaseModel):
    topic_name: str
    event_id: Optional[str] = None
    payload: Dict[str, Any]
    headers: Optional[Dict[str, Any]] = None
    partition_key: Optional[str] = None


class EventLogOut(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    topic_id: uuid.UUID
    topic_name: str
    event_id: str
    payload: Dict[str, Any]
    headers: Optional[Dict[str, Any]] = None
    status: str
    partition_key: Optional[str] = None
    is_replayed: bool
    published_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventReplayRequest(BaseModel):
    topic_name: str
    from_timestamp: Optional[datetime] = None
    to_timestamp: Optional[datetime] = None
    limit: int = 100


# ----------------------------------------------------
# Message Queue Schemas
# ----------------------------------------------------
class QueueMessagePublish(BaseModel):
    queue_name: str
    message_id: Optional[str] = None
    payload: Dict[str, Any]
    max_retries: int = 3


class QueueMessageOut(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    queue_name: str
    message_id: str
    payload: Dict[str, Any]
    status: str
    attempt_count: int
    max_retries: int
    consumer_id: Optional[str] = None
    error_details: Optional[str] = None
    processed_at: Optional[datetime] = None
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
    allowed_methods: List[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])


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
