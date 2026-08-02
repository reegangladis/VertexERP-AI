import abc
import asyncio
import json
import logging
import time
import uuid
from typing import Any

logger = logging.getLogger(__name__)


class BaseLLMProvider(abc.ABC):
    @abc.abstractmethod
    async def generate_response(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """
        Generate response from the LLM provider.
        Returns:
            {
                "content": str,
                "role": "assistant",
                "prompt_tokens": int,
                "completion_tokens": int,
                "tool_calls": list | None,
                "latency_ms": int
            }
        """
        pass


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None, model_name: str = "gpt-4o"):
        self.api_key = api_key
        self.model_name = model_name

    async def generate_response(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        start_time = time.time()
        # Fallback to Mock if API Key is missing
        if not self.api_key:
            return await MockLLMProvider(self.model_name).generate_response(
                messages, tools, temperature
            )

        try:
            import openai

            client = openai.AsyncOpenAI(api_key=self.api_key)
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
            }
            if tools:
                kwargs["tools"] = tools

            response = await client.chat.completions.create(**kwargs)
            choice = response.choices[0]

            tool_calls_list = None
            if choice.message.tool_calls:
                tool_calls_list = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in choice.message.tool_calls
                ]

            return {
                "content": choice.message.content or "",
                "role": "assistant",
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "tool_calls": tool_calls_list,
                "latency_ms": int((time.time() - start_time) * 1000),
            }
        except Exception as e:
            logger.error(
                f"OpenAI completion error: {e}. Falling back to mock response."
            )
            return await MockLLMProvider(self.model_name).generate_response(
                messages, tools, temperature
            )


class AzureOpenAIProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: str | None = None,
        endpoint: str | None = None,
        model_name: str = "gpt-4",
    ):
        self.api_key = api_key
        self.endpoint = endpoint
        self.model_name = model_name

    async def generate_response(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        start_time = time.time()
        if not self.api_key or not self.endpoint:
            return await MockLLMProvider(self.model_name).generate_response(
                messages, tools, temperature
            )

        try:
            import openai

            client = openai.AsyncAzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=self.endpoint,
                api_version="2024-02-15-preview",
            )
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
            }
            if tools:
                kwargs["tools"] = tools

            response = await client.chat.completions.create(**kwargs)
            choice = response.choices[0]

            tool_calls_list = None
            if choice.message.tool_calls:
                tool_calls_list = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in choice.message.tool_calls
                ]

            return {
                "content": choice.message.content or "",
                "role": "assistant",
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "tool_calls": tool_calls_list,
                "latency_ms": int((time.time() - start_time) * 1000),
            }
        except Exception as e:
            logger.error(f"Azure OpenAI completion error: {e}. Falling back to mock.")
            return await MockLLMProvider(self.model_name).generate_response(
                messages, tools, temperature
            )


class GeminiProvider(BaseLLMProvider):
    def __init__(
        self, api_key: str | None = None, model_name: str = "gemini-1.5-flash"
    ):
        self.api_key = api_key
        self.model_name = model_name

    async def generate_response(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        start_time = time.time()
        if not self.api_key:
            return await MockLLMProvider(self.model_name).generate_response(
                messages, tools, temperature
            )

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)

            # Map roles and prepare contents
            contents = []
            for msg in messages:
                role = "user" if msg["role"] in ["user", "system"] else "model"
                contents.append({"role": role, "parts": [msg["content"]]})

            response = await model.generate_content_async(
                contents=contents,
                generation_config=genai.types.GenerationConfig(temperature=temperature),
            )

            # Mock tokens count since gemini-genai doesn't always return counts directly
            prompt_tokens = int(sum(len(m["content"]) for m in messages) / 4)
            completion_tokens = int(len(response.text) / 4)

            return {
                "content": response.text,
                "role": "assistant",
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "tool_calls": None,
                "latency_ms": int((time.time() - start_time) * 1000),
            }
        except Exception as e:
            logger.error(f"Gemini API completion error: {e}. Falling back to mock.")
            return await MockLLMProvider(self.model_name).generate_response(
                messages, tools, temperature
            )


class AnthropicProvider(BaseLLMProvider):
    def __init__(
        self, api_key: str | None = None, model_name: str = "claude-3-5-sonnet"
    ):
        self.api_key = api_key
        self.model_name = model_name

    async def generate_response(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        start_time = time.time()
        if not self.api_key:
            return await MockLLMProvider(self.model_name).generate_response(
                messages, tools, temperature
            )

        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=self.api_key)

            # Extract system instruction
            system_instruction = ""
            chat_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system_instruction += msg["content"] + "\n"
                else:
                    chat_messages.append(
                        {"role": msg["role"], "content": msg["content"]}
                    )

            response = await client.messages.create(
                model=self.model_name,
                max_tokens=4000,
                temperature=temperature,
                system=system_instruction.strip() or None,
                messages=chat_messages,
            )

            return {
                "content": response.content[0].text if response.content else "",
                "role": "assistant",
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "tool_calls": None,
                "latency_ms": int((time.time() - start_time) * 1000),
            }
        except Exception as e:
            logger.error(f"Anthropic API completion error: {e}. Falling back to mock.")
            return await MockLLMProvider(self.model_name).generate_response(
                messages, tools, temperature
            )


class LocalModelProvider(BaseLLMProvider):
    def __init__(
        self, local_url: str = "http://localhost:11434", model_name: str = "llama3"
    ):
        self.local_url = local_url
        self.model_name = model_name

    async def generate_response(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        start_time = time.time()
        try:
            import httpx

            # Query Ollama style chat completion
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self.model_name,
                    "messages": messages,
                    "options": {"temperature": temperature},
                    "stream": False,
                }
                response = await client.post(
                    f"{self.local_url}/api/chat", json=payload, timeout=15.0
                )
                if response.status_code != 200:
                    raise RuntimeError(f"Ollama returned status {response.status_code}")

                result = response.json()
                content = result.get("message", {}).get("content", "")

                # Estimate token usage
                prompt_tokens = int(sum(len(m["content"]) for m in messages) / 4)
                completion_tokens = int(len(content) / 4)

                return {
                    "content": content,
                    "role": "assistant",
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "tool_calls": None,
                    "latency_ms": int((time.time() - start_time) * 1000),
                }
        except Exception as e:
            logger.warning(
                f"Local LLM client failure ({e}). Falling back to Mock generator."
            )
            return await MockLLMProvider(self.model_name).generate_response(
                messages, tools, temperature
            )


class MockLLMProvider(BaseLLMProvider):
    def __init__(self, model_name: str = "mock-gpt-4"):
        self.model_name = model_name

    async def generate_response(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        start_time = time.time()

        # Extract user message
        user_content = ""
        for m in reversed(messages):
            if m["role"] == "user":
                user_content = m["content"].lower()
                break

        # Check for specific intents and return structured mock replies or tool calls
        tool_calls = None
        content = ""

        # Intent Detection
        if "leave" in user_content or "time off" in user_content:
            # HR tool call mock or explanation
            if tools and any(
                t["function"]["name"] == "check_leave_balance" for t in tools
            ):
                tool_calls = [
                    {
                        "id": f"call_{uuid_str()[:8]}",
                        "type": "function",
                        "function": {
                            "name": "check_leave_balance",
                            "arguments": json.dumps(
                                {"employee_id": "current-user-emp"}
                            ),
                        },
                    }
                ]
            else:
                content = (
                    "To request leaves or verify your paid time off (PTO) balances, you can use the HR system. "
                    "According to company policy, standard employees start with 20 days of paid vacation per year."
                )

        elif (
            "lead" in user_content
            or "pipeline" in user_content
            or "crm" in user_content
        ):
            # CRM tool call mock
            if tools and any(
                t["function"]["name"] == "get_lead_details" for t in tools
            ):
                tool_calls = [
                    {
                        "id": f"call_{uuid_str()[:8]}",
                        "type": "function",
                        "function": {
                            "name": "get_lead_details",
                            "arguments": json.dumps({"limit": 5}),
                        },
                    }
                ]
            else:
                content = (
                    "I can help you review your active sales pipelines, customer interactions, and tickets. "
                    "Currently, CRM lead assignment rules enforce that high-priority enterprise deals are routed "
                    "directly to senior account executives within 24 hours of generation."
                )

        elif (
            "budget" in user_content
            or "invoice" in user_content
            or "spend" in user_content
        ):
            # Finance tool call mock
            if tools and any(
                t["function"]["name"] == "summarize_budget" for t in tools
            ):
                tool_calls = [
                    {
                        "id": f"call_{uuid_str()[:8]}",
                        "type": "function",
                        "function": {
                            "name": "summarize_budget",
                            "arguments": json.dumps({"fiscal_year": "2026"}),
                        },
                    }
                ]
            else:
                content = (
                    "Based on the fiscal year settings in the Finance Platform, budgets are tracked quarterly. "
                    "Would you like me to extract financial statements or retrieve budget caps for your department?"
                )

        elif (
            "inventory" in user_content
            or "stock" in user_content
            or "warehouse" in user_content
        ):
            # Inventory tool call mock
            if tools and any(t["function"]["name"] == "get_stock_level" for t in tools):
                tool_calls = [
                    {
                        "id": f"call_{uuid_str()[:8]}",
                        "type": "function",
                        "function": {
                            "name": "get_stock_level",
                            "arguments": json.dumps({"product_sku": "SKU-PROD-A"}),
                        },
                    }
                ]
            else:
                content = (
                    "Inventory levels across our core warehouses (Central-1 and Sub-East) are sync'd. "
                    "Let me know if you would like me to check stock availability or issue stock transfers."
                )

        elif (
            "bom" in user_content
            or "machine" in user_content
            or "manufacturing" in user_content
        ):
            # Manufacturing tool call mock
            if tools and any(t["function"]["name"] == "list_bom_items" for t in tools):
                tool_calls = [
                    {
                        "id": f"call_{uuid_str()[:8]}",
                        "type": "function",
                        "function": {
                            "name": "list_bom_items",
                            "arguments": json.dumps({"bom_id": "BOM-2026-X"}),
                        },
                    }
                ]
            else:
                content = (
                    "Our manufacturing facilities report operating capacities at 85% with 2 active routers. "
                    "Would you like to examine active production orders or fleet schedules?"
                )

        elif (
            "policy" in user_content
            or "document" in user_content
            or "manual" in user_content
            or "search" in user_content
        ):
            # RAG Search mock
            if tools and any(
                t["function"]["name"] == "search_knowledge_collection" for t in tools
            ):
                tool_calls = [
                    {
                        "id": f"call_{uuid_str()[:8]}",
                        "type": "function",
                        "function": {
                            "name": "search_knowledge_collection",
                            "arguments": json.dumps({"query": user_content}),
                        },
                    }
                ]
            else:
                content = (
                    "I can search our document collections vault to answer policy questions. "
                    "For example, the employee handbook states that travel expenses must be submitted within 30 days."
                )

        elif (
            "report" in user_content
            or "kpi" in user_content
            or "analytics" in user_content
        ):
            # BI report mock
            if tools and any(t["function"]["name"] == "get_kpi_value" for t in tools):
                tool_calls = [
                    {
                        "id": f"call_{uuid_str()[:8]}",
                        "type": "function",
                        "function": {
                            "name": "get_kpi_value",
                            "arguments": json.dumps({"kpi_code": "MRR_KPI"}),
                        },
                    }
                ]
            else:
                content = (
                    "The business intelligence dashboard contains key operational KPIs like Gross Margin, MRR, and "
                    "Employee Turnover. I can build reports or summarize the executives views on request."
                )

        else:
            # Generic response fallback
            content = (
                f"Hello! I am your VertexERP AI Copilot, running on {self.model_name}. I have access to live ERP APIs, "
                "knowledge search, and automated workflows. How can I assist you with HR, CRM, Finance, Inventory, or Manufacturing today?"
            )

        # Estimate mock tokens
        prompt_len = sum(len(m["content"]) for m in messages)
        prompt_tokens = int(prompt_len / 4)
        completion_tokens = int(len(content or str(tool_calls)) / 4)

        # Simulate realistic latency (100-300ms)
        await asyncio_sleep(0.1)
        latency = int((time.time() - start_time) * 1000)

        return {
            "content": content,
            "role": "assistant",
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "tool_calls": tool_calls,
            "latency_ms": latency,
        }


# --- Provider Factory ---
class LLMProviderRegistry:
    @staticmethod
    def get_provider(
        provider: str,
        model_name: str | None = None,
        api_key: str | None = None,
        endpoint: str | None = None,
        local_url: str | None = None,
    ) -> BaseLLMProvider:
        """
        Creates and returns the appropriate LLM provider adapter.
        """
        provider = provider.lower()
        if provider == "openai":
            return OpenAIProvider(api_key=api_key, model_name=model_name or "gpt-4o")
        elif provider == "azure_openai" or provider == "azure":
            return AzureOpenAIProvider(
                api_key=api_key, endpoint=endpoint, model_name=model_name or "gpt-4"
            )
        elif provider == "gemini":
            return GeminiProvider(
                api_key=api_key, model_name=model_name or "gemini-1.5-flash"
            )
        elif provider == "anthropic":
            return AnthropicProvider(
                api_key=api_key, model_name=model_name or "claude-3-5-sonnet"
            )
        elif provider == "local":
            return LocalModelProvider(
                local_url=local_url or "http://localhost:11434",
                model_name=model_name or "llama3",
            )
        else:
            return MockLLMProvider(model_name=model_name or "mock-model")


# Helpers
def uuid_str() -> str:
    return str(uuid.uuid4())


async def asyncio_sleep(sec: float):
    await asyncio.sleep(sec)
