import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


# --- Canvas Graph Models ---
class WorkflowNodePosition(BaseModel):
    x: float
    y: float


class WorkflowNodeData(BaseModel):
    label: str
    description: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)


class WorkflowNode(BaseModel):
    id: str
    type: str  # trigger, action, condition, approval, ai_copilot, rag_search, ml_prediction
    position: WorkflowNodePosition
    data: WorkflowNodeData


class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None
    condition_value: Optional[str] = None


class GraphDefinition(BaseModel):
    nodes: List[WorkflowNode] = Field(default_factory=list)
    edges: List[WorkflowEdge] = Field(default_factory=list)
    layout: Dict[str, Any] = Field(default_factory=dict)


# --- Workflow Schemas ---
class WorkflowBase(BaseModel):
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    category: str = Field(default="general")
    trigger_type: str = Field(default="manual")
    tags: Optional[List[str]] = None
    metadata_json: Optional[Dict[str, Any]] = None


class WorkflowCreate(WorkflowBase):
    graph_definition: Optional[GraphDefinition] = None


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    trigger_type: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    metadata_json: Optional[Dict[str, Any]] = None


class WorkflowResponse(WorkflowBase):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    status: str
    active_version_id: Optional[uuid.UUID] = None
    is_active: bool
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Workflow Version Schemas ---
class WorkflowVersionCreate(BaseModel):
    version_number: str
    graph_definition: GraphDefinition
    changelog: Optional[str] = None


class WorkflowVersionResponse(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    version_number: str
    graph_definition: Dict[str, Any]
    is_published: bool
    changelog: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Workflow Execution Schemas ---
class ExecutionTriggerRequest(BaseModel):
    trigger_type: str = Field(default="manual")
    input_payload: Dict[str, Any] = Field(default_factory=dict)


class WorkflowStepResponse(BaseModel):
    id: uuid.UUID
    execution_id: uuid.UUID
    step_key: str
    step_name: str
    step_type: str
    status: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    retry_count: int
    error_details: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionResponse(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    version_id: Optional[uuid.UUID] = None
    trigger_type: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    input_payload: Optional[Dict[str, Any]] = None
    output_payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    executed_by: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionDetailResponse(WorkflowExecutionResponse):
    steps: List[WorkflowStepResponse] = Field(default_factory=list)


# --- Template Schemas ---
class WorkflowTemplateCreate(BaseModel):
    name: str = Field(..., max_length=150)
    description: str
    category: str
    icon: Optional[str] = "Zap"
    graph_definition: GraphDefinition
    parameters: Optional[Dict[str, Any]] = None
    is_system: bool = False


class WorkflowTemplateResponse(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    name: str
    description: str
    category: str
    icon: Optional[str] = "Zap"
    graph_definition: Dict[str, Any]
    parameters: Optional[Dict[str, Any]] = None
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
    conditions: List[RuleCondition] = Field(default_factory=list)


class BusinessRuleCreate(BaseModel):
    name: str = Field(..., max_length=150)
    rule_group: str = Field(default="general")
    description: Optional[str] = None
    priority: int = Field(default=1)
    conditions_json: Dict[str, Any]
    actions_json: Dict[str, Any]
    is_active: bool = True


class BusinessRuleUpdate(BaseModel):
    name: Optional[str] = None
    rule_group: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    conditions_json: Optional[Dict[str, Any]] = None
    actions_json: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class BusinessRuleResponse(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    name: str
    rule_group: str
    description: Optional[str] = None
    priority: int
    conditions_json: Dict[str, Any]
    actions_json: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RuleEvaluationRequest(BaseModel):
    rule_group: Optional[str] = "general"
    context_data: Dict[str, Any]


class RuleEvaluationResult(BaseModel):
    evaluated_rules_count: int
    matched_rules_count: int
    triggered_actions: List[Dict[str, Any]] = Field(default_factory=list)
    matched_rule_ids: List[uuid.UUID] = Field(default_factory=list)


# --- Approval Schemas ---
class ApprovalRequestCreate(BaseModel):
    workflow_execution_id: Optional[uuid.UUID] = None
    step_key: Optional[str] = None
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    requester_id: str
    approver_id: Optional[str] = None
    approver_role: Optional[str] = None
    level: int = 1
    max_levels: int = 1
    due_date: Optional[datetime] = None
    escalation_user_id: Optional[str] = None


class ApprovalActionPayload(BaseModel):
    action: str  # approve, reject, delegate, escalate
    actor_id: str
    comments: Optional[str] = None
    delegate_to_user_id: Optional[str] = None
    escalate_to_user_id: Optional[str] = None


class ApprovalHistoryResponse(BaseModel):
    id: uuid.UUID
    approval_request_id: uuid.UUID
    action: str
    actor_id: str
    comments: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApprovalRequestResponse(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    workflow_execution_id: Optional[uuid.UUID] = None
    step_key: Optional[str] = None
    title: str
    description: Optional[str] = None
    requester_id: str
    approver_id: Optional[str] = None
    approver_role: Optional[str] = None
    level: int
    max_levels: int
    status: str
    due_date: Optional[datetime] = None
    escalation_user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Scheduler Schemas ---
class ScheduledJobCreate(BaseModel):
    workflow_id: uuid.UUID
    name: str = Field(..., max_length=150)
    schedule_type: str = Field(default="cron")  # cron, recurring, one_time, delayed
    cron_expression: Optional[str] = None
    next_run_at: Optional[datetime] = None
    payload: Optional[Dict[str, Any]] = None
    max_retries: int = 3


class ScheduledJobUpdate(BaseModel):
    name: Optional[str] = None
    schedule_type: Optional[str] = None
    cron_expression: Optional[str] = None
    next_run_at: Optional[datetime] = None
    status: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    max_retries: Optional[int] = None


class ScheduledJobResponse(BaseModel):
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    workflow_id: uuid.UUID
    name: str
    schedule_type: str
    cron_expression: Optional[str] = None
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    status: str
    payload: Optional[Dict[str, Any]] = None
    retry_count: int
    max_retries: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Log Schemas ---
class WorkflowLogResponse(BaseModel):
    id: uuid.UUID
    execution_id: uuid.UUID
    step_key: Optional[str] = None
    log_level: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
