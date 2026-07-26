"""
Phase 17 – Enterprise Workflow Automation Platform Unit Tests
Tests: Workflow Engine, Rule Engine, Approval Engine, Scheduler Service
"""
import uuid
import pytest
from datetime import datetime, UTC, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

# ─── Rule Engine Tests ──────────────────────────────────────────────────────────
from app.services.rule_engine import RuleEngine
from app.schemas.workflow import RuleEvaluationRequest


@pytest.fixture
def rule_engine():
    db_mock = AsyncMock()
    return RuleEngine(db_mock)


def test_rule_engine_simple_equality(rule_engine):
    result = rule_engine._compare("senior", "==", "senior")
    assert result is True


def test_rule_engine_inequality(rule_engine):
    result = rule_engine._compare("junior", "!=", "senior")
    assert result is True


def test_rule_engine_numeric_gte(rule_engine):
    result = rule_engine._compare(50000, ">=", 30000)
    assert result is True


def test_rule_engine_numeric_lt(rule_engine):
    result = rule_engine._compare(100, "<", 200)
    assert result is True


def test_rule_engine_contains(rule_engine):
    result = rule_engine._compare("Hello World", "contains", "World")
    assert result is True


def test_rule_engine_in_list(rule_engine):
    result = rule_engine._compare("admin", "in", ["admin", "manager", "cfo"])
    assert result is True


def test_rule_engine_not_in_list(rule_engine):
    result = rule_engine._compare("user", "not_in", ["admin", "manager"])
    assert result is True


def test_rule_engine_is_null(rule_engine):
    result = rule_engine._compare(None, "is_null", None)
    assert result is True


def test_rule_engine_is_not_null(rule_engine):
    result = rule_engine._compare("value", "is_not_null", None)
    assert result is True


def test_rule_engine_starts_with(rule_engine):
    result = rule_engine._compare("Finance Department", "starts_with", "Finance")
    assert result is True


def test_rule_engine_and_group(rule_engine):
    conditions_json = {
        "logical_operator": "AND",
        "conditions": [
            {"field": "amount", "operator": ">=", "value": 1000},
            {"field": "status", "operator": "==", "value": "pending"},
        ]
    }
    context = {"amount": 5000, "status": "pending"}
    result = rule_engine._evaluate_conditions(conditions_json, context)
    assert result is True


def test_rule_engine_and_group_fails(rule_engine):
    conditions_json = {
        "logical_operator": "AND",
        "conditions": [
            {"field": "amount", "operator": ">=", "value": 1000},
            {"field": "status", "operator": "==", "value": "approved"},  # mismatch
        ]
    }
    context = {"amount": 5000, "status": "pending"}
    result = rule_engine._evaluate_conditions(conditions_json, context)
    assert result is False


def test_rule_engine_or_group(rule_engine):
    conditions_json = {
        "logical_operator": "OR",
        "conditions": [
            {"field": "amount", "operator": ">=", "value": 100000},  # won't match
            {"field": "status", "operator": "==", "value": "pending"},   # matches
        ]
    }
    context = {"amount": 500, "status": "pending"}
    result = rule_engine._evaluate_conditions(conditions_json, context)
    assert result is True


def test_rule_engine_dot_notation(rule_engine):
    conditions_json = {
        "logical_operator": "AND",
        "conditions": [{"field": "invoice.amount", "operator": ">=", "value": 1000}]
    }
    context = {"invoice": {"amount": 5000}}
    result = rule_engine._evaluate_conditions(conditions_json, context)
    assert result is True


def test_rule_engine_schema_validation_valid(rule_engine):
    schema = {
        "logical_operator": "AND",
        "conditions": [{"field": "amount", "operator": ">=", "value": 1000}]
    }
    valid, msg = rule_engine.validate_conditions_schema(schema)
    assert valid is True


def test_rule_engine_schema_validation_invalid_operator(rule_engine):
    schema = {
        "conditions": [{"field": "amount", "operator": "UNKNOWN", "value": 1000}]
    }
    valid, msg = rule_engine.validate_conditions_schema(schema)
    assert valid is False
    assert "UNKNOWN" in msg


def test_rule_engine_schema_validation_missing_field(rule_engine):
    schema = {
        "conditions": [{"operator": "=="}]  # missing 'field'
    }
    valid, msg = rule_engine.validate_conditions_schema(schema)
    assert valid is False


# ─── Approval Engine Tests ───────────────────────────────────────────────────────
from app.services.approval_engine import ApprovalEngine
from app.schemas.workflow import ApprovalRequestCreate, ApprovalActionPayload
from app.models.workflow import ApprovalRequest


@pytest.fixture
def approval_engine():
    db_mock = AsyncMock()
    engine = ApprovalEngine(db_mock)
    engine.repo = MagicMock()
    return engine


@pytest.mark.asyncio
async def test_create_approval_request(approval_engine):
    org_id = uuid.uuid4()
    approval_engine.repo.create_approval = AsyncMock(return_value=ApprovalRequest(
        id=uuid.uuid4(),
        title="Test Approval",
        requester_id="user1",
        status="pending",
        level=1,
        max_levels=2,
    ))
    approval_engine.repo.create_approval_history = AsyncMock(return_value=MagicMock())
    approval_engine.db.commit = AsyncMock()

    data = ApprovalRequestCreate(
        title="Test Approval",
        requester_id="user1",
        level=1,
        max_levels=2,
    )
    result = await approval_engine.create_approval_request(org_id, data)
    assert result.title == "Test Approval"
    assert approval_engine.repo.create_approval.called


@pytest.mark.asyncio
async def test_process_approval_action_approve_single_level(approval_engine):
    org_id = uuid.uuid4()
    approval_id = uuid.uuid4()

    mock_approval = ApprovalRequest(
        id=approval_id,
        title="Test",
        requester_id="user1",
        status="pending",
        level=1,
        max_levels=1,
    )
    approval_engine.repo.get_approval = AsyncMock(return_value=mock_approval)
    approval_engine.repo.update_approval = AsyncMock(side_effect=lambda obj, updates: setattr(obj, 'status', updates.get('status', obj.status)) or obj)
    approval_engine.repo.create_approval_history = AsyncMock(return_value=MagicMock())
    approval_engine.db.commit = AsyncMock()

    payload = ApprovalActionPayload(action="approve", actor_id="manager1")
    result = await approval_engine.process_action(org_id, approval_id, payload)
    assert approval_engine.repo.update_approval.called


@pytest.mark.asyncio
async def test_process_approval_action_reject(approval_engine):
    org_id = uuid.uuid4()
    approval_id = uuid.uuid4()
    mock_approval = ApprovalRequest(id=approval_id, title="Test", requester_id="user1", status="pending", level=1, max_levels=1)
    approval_engine.repo.get_approval = AsyncMock(return_value=mock_approval)
    approval_engine.repo.update_approval = AsyncMock(return_value=mock_approval)
    approval_engine.repo.create_approval_history = AsyncMock(return_value=MagicMock())
    approval_engine.db.commit = AsyncMock()

    payload = ApprovalActionPayload(action="reject", actor_id="manager1", comments="Budget exceeded")
    await approval_engine.process_action(org_id, approval_id, payload)
    approval_engine.repo.update_approval.assert_called()


@pytest.mark.asyncio
async def test_process_approval_delegate(approval_engine):
    org_id = uuid.uuid4()
    approval_id = uuid.uuid4()
    mock_approval = ApprovalRequest(id=approval_id, title="Test", requester_id="user1", status="pending", level=1, max_levels=1)
    approval_engine.repo.get_approval = AsyncMock(return_value=mock_approval)
    approval_engine.repo.update_approval = AsyncMock(return_value=mock_approval)
    approval_engine.repo.create_approval_history = AsyncMock(return_value=MagicMock())
    approval_engine.db.commit = AsyncMock()

    payload = ApprovalActionPayload(action="delegate", actor_id="manager1", delegate_to_user_id="delegate_user")
    await approval_engine.process_action(org_id, approval_id, payload)
    assert approval_engine.repo.update_approval.called


# ─── Scheduler Tests ─────────────────────────────────────────────────────────────
from app.services.scheduler_service import SchedulerService
from app.schemas.workflow import ScheduledJobCreate


@pytest.fixture
def scheduler():
    db_mock = AsyncMock()
    svc = SchedulerService(db_mock)
    svc.repo = MagicMock()
    return svc


def test_scheduler_compute_next_run_cron(scheduler):
    next_run = scheduler._compute_next_run("*/5 * * * *", "cron")
    assert next_run is not None
    assert next_run > datetime.now(UTC)


def test_scheduler_compute_next_run_one_time(scheduler):
    next_run = scheduler._compute_next_run(None, "one_time")
    assert next_run is None


def test_scheduler_compute_next_run_delayed(scheduler):
    next_run = scheduler._compute_next_run(None, "delayed")
    assert next_run is not None
    assert next_run > datetime.now(UTC)


def test_scheduler_cron_interval_parsing(scheduler):
    """Test simplified interval cron parsing fallback (*/5 = 5 minutes)."""
    after = datetime.now(UTC)
    next_run = scheduler._parse_cron_next("*/15 * * * *", after)
    assert next_run is not None
    diff = (next_run - after).total_seconds()
    assert 14 * 60 <= diff <= 16 * 60  # approximately 15 minutes


def test_calculate_next_run_public_api(scheduler):
    result = scheduler.calculate_next_run("0 8 * * *")
    # Should return an ISO datetime string or None
    assert result is None or isinstance(result, str)


@pytest.mark.asyncio
async def test_scheduler_create_job(scheduler):
    workflow_id = uuid.uuid4()
    from app.models.workflow import ScheduledJob
    mock_job = ScheduledJob(
        id=uuid.uuid4(),
        workflow_id=workflow_id,
        name="Test Job",
        schedule_type="cron",
        cron_expression="0 8 * * *",
        status="active",
        retry_count=0,
        max_retries=3,
    )
    scheduler.repo.create_scheduled_job = AsyncMock(return_value=mock_job)
    scheduler.db.commit = AsyncMock()

    data = ScheduledJobCreate(
        workflow_id=workflow_id,
        name="Test Job",
        schedule_type="cron",
        cron_expression="0 8 * * *",
    )
    result = await scheduler.create_job(None, data)
    assert result.name == "Test Job"
    assert scheduler.repo.create_scheduled_job.called


# ─── Workflow Engine Tests ───────────────────────────────────────────────────────
from app.services.workflow_engine import WorkflowEngine


@pytest.fixture
def workflow_engine():
    db_mock = AsyncMock()
    engine = WorkflowEngine(db_mock)
    engine.repo = MagicMock()
    return engine


def test_workflow_engine_compare_equal(workflow_engine):
    assert workflow_engine._compare("hello", "==", "hello") is True


def test_workflow_engine_compare_numeric(workflow_engine):
    assert workflow_engine._compare(100, ">", 50) is True
    assert workflow_engine._compare(10, "<=", 10) is True


def test_workflow_engine_find_entry_nodes_no_incoming(workflow_engine):
    nodes = [{"id": "n1"}, {"id": "n2"}, {"id": "n3"}]
    edges = [{"source": "n1", "target": "n2"}, {"source": "n2", "target": "n3"}]
    entries = workflow_engine._find_entry_nodes(nodes, edges)
    assert entries == ["n1"]


def test_workflow_engine_build_adjacency(workflow_engine):
    nodes = [{"id": "n1"}, {"id": "n2"}]
    edges = [{"source": "n1", "target": "n2", "id": "e1"}]
    adj = workflow_engine._build_adjacency(nodes, edges)
    assert "n1" in adj
    assert len(adj["n1"]) == 1
    assert adj["n1"][0]["target"] == "n2"


@pytest.mark.asyncio
async def test_handle_trigger_returns_triggered(workflow_engine):
    result = await workflow_engine._handle_trigger({"trigger_type": "manual"}, {})
    assert result["__triggered__"] is True


@pytest.mark.asyncio
async def test_handle_condition_if_else_true(workflow_engine):
    config = {"condition_type": "if_else", "field": "status", "operator": "==", "value": "pending"}
    context = {"status": "pending"}
    result = await workflow_engine._handle_condition(config, context)
    assert result["__branch__"] == "true"


@pytest.mark.asyncio
async def test_handle_condition_if_else_false(workflow_engine):
    config = {"condition_type": "if_else", "field": "amount", "operator": ">=", "value": 10000}
    context = {"amount": 100}
    result = await workflow_engine._handle_condition(config, context)
    assert result["__branch__"] == "false"


@pytest.mark.asyncio
async def test_handle_ai_copilot(workflow_engine):
    config = {"prompt": "Summarize this employee profile"}
    result = await workflow_engine._handle_ai_copilot(config, {})
    assert result["ai_copilot_executed"] is True
    assert result["prompt"] == "Summarize this employee profile"


@pytest.mark.asyncio
async def test_handle_rag_search(workflow_engine):
    config = {"query": "Company onboarding policy"}
    result = await workflow_engine._handle_rag_search(config, {})
    assert result["rag_search_executed"] is True


@pytest.mark.asyncio
async def test_handle_ml_prediction(workflow_engine):
    config = {"model_id": "churn-predictor-v2"}
    result = await workflow_engine._handle_ml_prediction(config, {})
    assert result["ml_prediction_executed"] is True
    assert result["model_id"] == "churn-predictor-v2"


@pytest.mark.asyncio
async def test_elapsed_ms(workflow_engine):
    import time
    start = datetime.now(UTC)
    time.sleep(0.01)
    ms = workflow_engine._elapsed_ms(start)
    assert ms >= 10  # at least 10ms
