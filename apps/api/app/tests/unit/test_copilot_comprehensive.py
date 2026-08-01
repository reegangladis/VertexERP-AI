import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from app.services.copilot.llm_provider import LLMProviderRegistry, MockLLMProvider
from app.services.copilot.tools import registry as tool_registry
from app.services.copilot.engine import PromptManager, ContextManager
from app.schemas.copilot import CopilotSessionCreate, ChatRequest, PromptTestRequest


@pytest.mark.asyncio
async def test_llm_provider_registry():
    provider_openai = LLMProviderRegistry.get_provider("openai", model_name="gpt-4o")
    assert provider_openai is not None

    provider_mock = LLMProviderRegistry.get_provider("mock", model_name="mock-model")
    assert isinstance(provider_mock, MockLLMProvider)

    resp = await provider_mock.generate_response(
        messages=[{"role": "user", "content": "Show me my vacation leave balance"}]
    )

    assert "role" in resp
    assert resp["role"] == "assistant"
    assert resp["prompt_tokens"] > 0


@pytest.mark.asyncio
async def test_prompt_manager_rendering():
    template = "Hello {{ user_name }}, welcome to {{ org_name }} (ID: {{ org_id }})."
    variables = {
        "user_name": "Sarah Connor",
        "org_name": "VertexERP Corp",
        "org_id": "ORG-1001"
    }

    rendered = PromptManager.render_template(template, variables)
    assert "Sarah Connor" in rendered
    assert "VertexERP Corp" in rendered
    assert "ORG-1001" in rendered


@pytest.mark.asyncio
async def test_tool_registry_executors():
    db_mock = AsyncMock()
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Test HR Leave tool
    res_hr = await tool_registry.execute(
        name="check_leave_balance",
        arguments={"employee_id": "emp-101"},
        db=db_mock,
        org_id=org_id,
        user_id=user_id
    )
    assert res_hr["status"] == "success"
    assert "vacation_days_remaining" in res_hr["result"]

    # Test CRM Leads tool
    res_crm = await tool_registry.execute(
        name="get_lead_details",
        arguments={"limit": 3},
        db=db_mock,
        org_id=org_id,
        user_id=user_id
    )
    assert res_crm["status"] == "success"
    assert isinstance(res_crm["result"], list)

    # Test Inventory Stock tool
    res_inv = await tool_registry.execute(
        name="get_stock_level",
        arguments={"product_sku": "SKU-PROD-A"},
        db=db_mock,
        org_id=org_id,
        user_id=user_id
    )
    assert res_inv["status"] == "success"
    assert "total_quantity" in res_inv["result"]

    # Test Finance Budget tool
    res_fin = await tool_registry.execute(
        name="summarize_budget",
        arguments={"fiscal_year": "2026"},
        db=db_mock,
        org_id=org_id,
        user_id=user_id
    )
    assert res_fin["status"] == "success"
    assert "total_allocated_budget" in res_fin["result"]

    # Test Manufacturing BOM tool
    res_mfg = await tool_registry.execute(
        name="list_bom_items",
        arguments={"bom_id": "BOM-2026-X"},
        db=db_mock,
        org_id=org_id,
        user_id=user_id
    )
    assert res_mfg["status"] == "success"
    assert "raw_materials" in res_mfg["result"]

    # Test Analytics KPI tool
    res_bi = await tool_registry.execute(
        name="get_kpi_value",
        arguments={"kpi_code": "MRR_KPI"},
        db=db_mock,
        org_id=org_id,
        user_id=user_id
    )
    assert res_bi["status"] == "success"
    assert "current_value" in res_bi["result"]


@pytest.mark.asyncio
async def test_context_manager_compilation():
    system_prompt = "You are VertexERP AI Assistant."
    history = [
        {"role": "user", "content": "What is our Q2 revenue?"},
        {"role": "assistant", "content": "Q2 Revenue is $1.2M."}
    ]

    compiled = ContextManager.compile_history(system_prompt, history, max_messages=15)
    assert len(compiled) == 3
    assert compiled[0]["role"] == "system"
    assert compiled[1]["role"] == "user"
    assert compiled[2]["role"] == "assistant"
