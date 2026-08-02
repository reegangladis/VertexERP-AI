import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# --- Canvas Graph Models ---
class WorkflowNodePosition(BaseModel):
    x: float
    y: float


class WorkflowNodeData(BaseModel):
    label: str
    description: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class WorkflowNode(BaseModel):
    id: str
    type: str  # trigger, action, condition, approval, ai_copilot, rag_search, ml_prediction
    position: WorkflowNodePosition
    data: WorkflowNodeData


class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str | None = None
    condition_value: str | None = None


class GraphDefinition(BaseModel):
    nodes: list[WorkflowNode] = Field(default_factory=list)
    edges: list[WorkflowEdge] = Field(default_factory=list)
    layout: dict[str, Any] = Field(default_factory=dict)


# --- Workflow Schemas ---
class WorkflowBase(BaseModel):
    name: str = Field(..., max_length=150)
    description: str | None = None
    category: str = Field(default="general")
    trigger_type: str = Field(default="manual")
    tags: list[str] | None = None
    metadata_json: dict[str, Any] | None = None


class WorkflowCreate(WorkflowBase):
    graph_definition: GraphDefinition | None = None


class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    trigger_type: str | None = None
    status: str | None = None
    is_active: bool | None = None
    tags: list[str] | None = None
    metadata_json: dict[str, Any] | None = None


class WorkflowResponse(WorkflowBase):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    status: str
    active_version_id: uuid.UUID | None = None
    is_active: bool
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Workflow Version Schemas ---
class WorkflowVersionCreate(BaseModel):
    version_number: str
    graph_definition: GraphDefinition
    changelog: str | None = None


class WorkflowVersionResponse(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    organization_id: uuid.UUID | None = None
    version_number: str
    graph_definition: dict[str, Any]
    is_published: bool
    changelog: str | None = None
    created_by: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Workflow Execution Schemas ---
class ExecutionTriggerRequest(BaseModel):
    trigger_type: str = Field(default="manual")
    input_payload: dict[str, Any] = Field(default_factory=dict)


class WorkflowStepResponse(BaseModel):
    id: uuid.UUID
    execution_id: uuid.UUID
    step_key: str
    step_name: str
    step_type: str
    status: str
    input_data: dict[str, Any] | None = None
    output_data: dict[str, Any] | None = None
    duration_ms: float | None = None
    retry_count: int
    error_details: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionResponse(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    version_id: uuid.UUID | None = None
    trigger_type: str
    status: str
    start_time: datetime
    end_time: datetime | None = None
    duration_ms: float | None = None
    input_payload: dict[str, Any] | None = None
    output_payload: dict[str, Any] | None = None
    error_message: str | None = None
    executed_by: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionDetailResponse(WorkflowExecutionResponse):
    steps: list[WorkflowStepResponse] = Field(default_factory=list)


# --- Template Schemas ---
class WorkflowTemplateCreate(BaseModel):
    name: str = Field(..., max_length=150)
    description: str
    category: str
    icon: str | None = "Zap"
    graph_definition: GraphDefinition
    parameters: dict[str, Any] | None = None
    is_system: bool = False


class WorkflowTemplateResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    name: str
    description: str
    category: str
    icon: str | None = "Zap"
    graph_definition: dict[str, Any]
    parameters: dict[str, Any] | None = None
    is_system: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Business Rule Schemas ---
class RuleCondition(BaseModel):
    field: str
    operator: str  # ==, !=, >, <, >=, <=, in, contains, matches
    value: Any


class RuleConditionGroup(BaseModel):
    logical_operator: str = Field(default="AND")  # AND, OR
    conditions: list[RuleCondition] = Field(default_factory=list)


class BusinessRuleCreate(BaseModel):
    name: str = Field(..., max_length=150)
    rule_group: str = Field(default="general")
    description: str | None = None
    priority: int = Field(default=1)
    conditions_json: dict[str, Any]
    actions_json: dict[str, Any]
    is_active: bool = True


class BusinessRuleUpdate(BaseModel):
    name: str | None = None
    rule_group: str | None = None
    description: str | None = None
    priority: int | None = None
    conditions_json: dict[str, Any] | None = None
    actions_json: dict[str, Any] | None = None
    is_active: bool | None = None


class BusinessRuleResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    name: str
    rule_group: str
    description: str | None = None
    priority: int
    conditions_json: dict[str, Any]
    actions_json: dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RuleEvaluationRequest(BaseModel):
    rule_group: str | None = "general"
    context_data: dict[str, Any]


class RuleEvaluationResult(BaseModel):
    evaluated_rules_count: int
    matched_rules_count: int
    triggered_actions: list[dict[str, Any]] = Field(default_factory=list)
    matched_rule_ids: list[uuid.UUID] = Field(default_factory=list)


# --- Approval Schemas ---
class ApprovalRequestCreate(BaseModel):
    workflow_execution_id: uuid.UUID | None = None
    step_key: str | None = None
    title: str = Field(..., max_length=200)
    description: str | None = None
    requester_id: str
    approver_id: str | None = None
    approver_role: str | None = None
    level: int = 1
    max_levels: int = 1
    due_date: datetime | None = None
    escalation_user_id: str | None = None


class ApprovalActionPayload(BaseModel):
    action: str  # approve, reject, delegate, escalate
    actor_id: str
    comments: str | None = None
    delegate_to_user_id: str | None = None
    escalate_to_user_id: str | None = None


class ApprovalHistoryResponse(BaseModel):
    id: uuid.UUID
    approval_request_id: uuid.UUID
    action: str
    actor_id: str
    comments: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApprovalRequestResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    workflow_execution_id: uuid.UUID | None = None
    step_key: str | None = None
    title: str
    description: str | None = None
    requester_id: str
    approver_id: str | None = None
    approver_role: str | None = None
    level: int
    max_levels: int
    status: str
    due_date: datetime | None = None
    escalation_user_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Scheduler Schemas ---
class ScheduledJobCreate(BaseModel):
    workflow_id: uuid.UUID
    name: str = Field(..., max_length=150)
    schedule_type: str = Field(default="cron")  # cron, recurring, one_time, delayed
    cron_expression: str | None = None
    next_run_at: datetime | None = None
    payload: dict[str, Any] | None = None
    max_retries: int = 3


class ScheduledJobUpdate(BaseModel):
    name: str | None = None
    schedule_type: str | None = None
    cron_expression: str | None = None
    next_run_at: datetime | None = None
    status: str | None = None
    payload: dict[str, Any] | None = None
    max_retries: int | None = None


class ScheduledJobResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    workflow_id: uuid.UUID
    name: str
    schedule_type: str
    cron_expression: str | None = None
    next_run_at: datetime | None = None
    last_run_at: datetime | None = None
    status: str
    payload: dict[str, Any] | None = None
    retry_count: int
    max_retries: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Log Schemas ---
class WorkflowLogResponse(BaseModel):
    id: uuid.UUID
    execution_id: uuid.UUID
    step_key: str | None = None
    log_level: str
    message: str
    details: dict[str, Any] | None = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
