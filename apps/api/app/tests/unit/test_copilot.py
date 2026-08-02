import uuid

import pytest

from app.services.copilot.engine import (
    ContextManager,
    PIIMasker,
    PromptManager,
    RedisRateLimiter,
)
from app.services.copilot.llm_provider import LLMProviderRegistry, MockLLMProvider
from app.services.copilot.tools import registry as tool_registry


@pytest.mark.asyncio
async def test_llm_provider_registry_and_mock():
    # Fetch mock provider
    llm = LLMProviderRegistry.get_provider("mock", "mock-gpt-4")
    assert isinstance(llm, MockLLMProvider)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "I want to check my leave balances please."},
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "check_leave_balance",
                "description": "Check employee leave",
                "parameters": {},
            },
        }
    ]

    response = await llm.generate_response(messages, tools)
    assert response["role"] == "assistant"
    assert response["latency_ms"] >= 0
    assert response["prompt_tokens"] > 0
    # The mock provider should detect 'leave' in content and output tool_calls
    assert response["tool_calls"] is not None
    assert response["tool_calls"][0]["function"]["name"] == "check_leave_balance"


@pytest.mark.asyncio
async def test_tool_registry_and_execution():
    # Verify check_leave_balance tool is registered
    tool = tool_registry.get_tool("check_leave_balance")
    assert tool is not None
    assert tool["required_role"] == "hr.view"

    # Mock Async Database session
    class MockSession:
        async def execute(self, query):
            class Result:
                def scalars(self):
                    class Scalars:
                        def first(self):
                            return None

                    return Scalars()

                def scalar_one_or_none(self):
                    return None

            return Result()

    mock_db = MockSession()
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Execute tool
    resp = await tool_registry.execute(
        name="check_leave_balance",
        arguments={"employee_id": "current"},
        db=mock_db,
        org_id=org_id,
        user_id=user_id,
    )

    assert resp["status"] == "success"
    # Even if DB is empty, check_leave_balance has a mock fallback returning balances
    assert resp["result"]["vacation_days_allocated"] == 20
    assert resp["result"]["vacation_days_remaining"] > 0


def test_prompt_rendering():
    template = "Hello {{ user_name }} from {{ org_name }}. Welcome!"
    variables = {"user_name": "Alice Developer", "org_name": "Antigravity Corp"}
    rendered = PromptManager.render_template(template, variables)
    assert rendered == "Hello Alice Developer from Antigravity Corp. Welcome!"

    # Verify fallback handles missing variables gracefully
    default_prompt = PromptManager.get_default_prompt("hr")
    assert "HR Intelligence" in default_prompt


def test_pii_data_masking():
    sensitive_text = (
        "Employee SSN is 123-45-6789. Contact phone is 555-019-2834. "
        "Email matches support@vertexerp.io. Salary details: salary is $125,000.00 yearly."
    )

    # User is standard worker (gets masked)
    masked = PIIMasker.mask(sensitive_text, ["Developer", "Support Agent"])
    assert "123-45-6789" not in masked
    assert "555-019-2834" not in masked
    assert "support@vertexerp.io" not in masked
    assert "125,000.00" not in masked
    assert "[SSN MASKED]" in masked
    assert "[PHONE MASKED]" in masked
    assert "[EMAIL MASKED]" in masked
    assert "[CONFIDENTIAL]" in masked

    # User is Admin / HR Manager (does NOT get masked)
    unmasked = PIIMasker.mask(sensitive_text, ["HR Manager"])
    assert "123-45-6789" in unmasked
    assert "555-019-2834" in unmasked
    assert "support@vertexerp.io" in unmasked
    assert "125,000.00" in unmasked


def test_conversation_history_sliding_window():
    system_prompt = "System rule"
    chat_history = [
        {"role": "user", "content": "Msg 1"},
        {"role": "assistant", "content": "Reply 1"},
        {"role": "user", "content": "Msg 2"},
        {"role": "assistant", "content": "Reply 2"},
        {"role": "user", "content": "Msg 3"},
        {"role": "assistant", "content": "Reply 3"},
    ]

    # Compile with sliding window max of 4 messages
    compiled = ContextManager.compile_history(
        system_prompt, chat_history, max_messages=4
    )
    assert len(compiled) == 5  # 1 system + 4 recent history
    assert compiled[0]["role"] == "system"
    assert compiled[1]["content"] == "Msg 2"
    assert compiled[4]["content"] == "Reply 3"


@pytest.mark.asyncio
async def test_redis_rate_limiting():
    # Mock Redis client
    class MockRedisClient:
        def __init__(self):
            self.store = {}

        async def get(self, key):
            return self.store.get(key)

        async def set(self, key, val, ex=60):
            self.store[key] = val

        async def incr(self, key):
            self.store[key] = int(self.store[key]) + 1

    class MockRedisService:
        def __init__(self):
            self.client = MockRedisClient()

    redis_service = MockRedisService()
    uid = uuid.uuid4()

    # Call 1: Success
    limit_hit = await RedisRateLimiter.is_rate_limited(redis_service, uid, limit=3)
    assert limit_hit is False

    # Call 2: Success
    limit_hit = await RedisRateLimiter.is_rate_limited(redis_service, uid, limit=3)
    assert limit_hit is False

    # Call 3: Limit hit
    limit_hit = await RedisRateLimiter.is_rate_limited(redis_service, uid, limit=2)
    assert limit_hit is True
