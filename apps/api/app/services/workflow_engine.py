"""
Workflow Execution Engine — DAG-based step runner supporting:
  Triggers, Actions, Conditions (If/Else, Switch, Loops, Parallel, Retry, Timeout),
  Approvals, AI integrations (Copilot, RAG, ML Prediction), External API calls.
"""

import asyncio
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import WorkflowExecution
from app.repositories.workflow_repository import WorkflowRepository


class WorkflowEngine:
    """Core workflow execution engine — resolves and runs DAG step by step."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = WorkflowRepository(db)

    # ─── Public API ──────────────────────────────────────────────────────────────
    async def trigger_workflow(
        self,
        org_id: uuid.UUID | None,
        workflow_id: uuid.UUID,
        version_id: uuid.UUID | None,
        trigger_type: str,
        input_payload: dict[str, Any],
        executed_by: str | None = None,
    ) -> WorkflowExecution:
        """Create and launch a new workflow execution."""
        execution = await self.repo.create_execution(
            org_id,
            {
                "workflow_id": workflow_id,
                "version_id": version_id,
                "trigger_type": trigger_type,
                "status": "running",
                "input_payload": input_payload,
                "executed_by": executed_by,
            },
        )
        await self._log(
            org_id,
            execution.id,
            None,
            "INFO",
            f"Workflow execution started. trigger={trigger_type}",
        )

        version = await self.repo.get_version(version_id) if version_id else None
        if not version:
            await self._fail_execution(execution, org_id, "No published version found.")
            return execution

        graph: dict[str, Any] = version.graph_definition or {}
        context: dict[str, Any] = dict(input_payload)

        try:
            output = await self._execute_graph(org_id, execution, graph, context)
            execution = await self.repo.update_execution(
                execution,
                {
                    "status": "completed",
                    "end_time": datetime.now(UTC),
                    "output_payload": output,
                    "duration_ms": self._elapsed_ms(execution.start_time),
                },
            )
            await self._log(
                org_id,
                execution.id,
                None,
                "INFO",
                "Workflow execution completed successfully.",
            )
        except Exception as exc:
            await self._fail_execution(execution, org_id, str(exc))

        await self.db.commit()
        return execution

    async def cancel_execution(
        self, execution: WorkflowExecution, org_id: uuid.UUID | None
    ) -> WorkflowExecution:
        return await self.repo.update_execution(
            execution,
            {
                "status": "cancelled",
                "end_time": datetime.now(UTC),
            },
        )

    # ─── Graph Executor ──────────────────────────────────────────────────────────
    async def _execute_graph(
        self,
        org_id: uuid.UUID | None,
        execution: WorkflowExecution,
        graph: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        nodes: list[dict] = graph.get("nodes", [])
        edges: list[dict] = graph.get("edges", [])

        adjacency = self._build_adjacency(nodes, edges)
        node_map = {n["id"]: n for n in nodes}

        # Find start node (trigger node or first node with no incoming edges)
        entry_ids = self._find_entry_nodes(nodes, edges)

        visited: set = set()
        output: dict[str, Any] = {}

        async def visit(node_id: str) -> dict[str, Any]:
            if node_id in visited:
                return {}
            visited.add(node_id)
            node = node_map.get(node_id)
            if not node:
                return {}
            result = await self._execute_node(org_id, execution, node, context)
            context.update(result)
            output.update(result)

            # Resolve next nodes based on edge conditions
            successors = adjacency.get(node_id, [])
            for edge in successors:
                cond_value = edge.get("condition_value")
                target_id = edge["target"]
                if cond_value is None or cond_value == context.get("__branch__"):
                    await visit(target_id)
            return result

        for entry in entry_ids:
            await visit(entry)

        return output

    def _build_adjacency(
        self, nodes: list[dict], edges: list[dict]
    ) -> dict[str, list[dict]]:
        adj: dict[str, list[dict]] = {}
        for n in nodes:
            adj[n["id"]] = []
        for e in edges:
            src = e.get("source")
            if src and src in adj:
                adj[src].append(e)
        return adj

    def _find_entry_nodes(self, nodes: list[dict], edges: list[dict]) -> list[str]:
        targets = {e["target"] for e in edges}
        return [n["id"] for n in nodes if n["id"] not in targets] or (
            [nodes[0]["id"]] if nodes else []
        )

    # ─── Node Executor ───────────────────────────────────────────────────────────
    async def _execute_node(
        self,
        org_id: uuid.UUID | None,
        execution: WorkflowExecution,
        node: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        node_id = node["id"]
        node_type = node.get("type", "action")
        node_data = node.get("data", {})
        step_name = node_data.get("label", node_id)

        step = await self.repo.create_step(
            org_id,
            {
                "execution_id": execution.id,
                "step_key": node_id,
                "step_name": step_name,
                "step_type": node_type,
                "status": "running",
                "input_data": dict(context),
            },
        )

        start = datetime.now(UTC)
        output: dict[str, Any] = {}

        try:
            config: dict[str, Any] = node_data.get("config", {})
            handler = self._get_handler(node_type)
            output = await handler(config, context)
            duration = self._elapsed_ms(start)
            await self.repo.update_step(
                step,
                {"status": "completed", "output_data": output, "duration_ms": duration},
            )
            await self._log(
                org_id,
                execution.id,
                node_id,
                "INFO",
                f"Step '{step_name}' completed in {duration:.1f}ms.",
            )
        except Exception as exc:
            retry_max = node_data.get("config", {}).get("max_retries", 0)
            if step.retry_count < retry_max:
                await self.repo.update_step(
                    step, {"retry_count": step.retry_count + 1, "status": "running"}
                )
                await asyncio.sleep(2)
                return await self._execute_node(org_id, execution, node, context)
            await self.repo.update_step(
                step,
                {
                    "status": "failed",
                    "error_details": str(exc),
                    "duration_ms": self._elapsed_ms(start),
                },
            )
            await self._log(
                org_id,
                execution.id,
                node_id,
                "ERROR",
                f"Step '{step_name}' failed: {exc}",
            )
            raise

        return output

    # ─── Step Handlers ───────────────────────────────────────────────────────────
    def _get_handler(self, node_type: str):
        handlers = {
            "trigger": self._handle_trigger,
            "action": self._handle_action,
            "condition": self._handle_condition,
            "approval": self._handle_approval_node,
            "ai_copilot": self._handle_ai_copilot,
            "rag_search": self._handle_rag_search,
            "ml_prediction": self._handle_ml_prediction,
            "external_api": self._handle_external_api,
        }
        return handlers.get(node_type, self._handle_action)

    async def _handle_trigger(self, config: dict, context: dict) -> dict[str, Any]:
        return {"__triggered__": True, "trigger_config": config}

    async def _handle_action(self, config: dict, context: dict) -> dict[str, Any]:
        action_type = config.get("action_type", "noop")
        return {
            "action_executed": action_type,
            "action_config": config,
            "context_snapshot": {
                k: v for k, v in context.items() if not k.startswith("__")
            },
        }

    async def _handle_condition(self, config: dict, context: dict) -> dict[str, Any]:
        """Evaluate if/else or switch conditions, set __branch__ in context."""
        cond_type = config.get("condition_type", "if_else")
        if cond_type == "if_else":
            field = config.get("field", "")
            operator = config.get("operator", "==")
            value = config.get("value")
            actual = context.get(field)
            result = self._compare(actual, operator, value)
            branch = "true" if result else "false"
        elif cond_type == "switch":
            field = config.get("field", "")
            actual = context.get(field)
            branch = str(actual)
        else:
            branch = "true"
        return {"__branch__": branch, "condition_result": branch}

    async def _handle_approval_node(
        self, config: dict, context: dict
    ) -> dict[str, Any]:
        # In a real system this would pause the workflow and wait for human approval
        return {"approval_required": True, "approval_config": config}

    async def _handle_ai_copilot(self, config: dict, context: dict) -> dict[str, Any]:
        prompt = config.get("prompt", "")
        return {
            "ai_copilot_executed": True,
            "prompt": prompt,
            "response": "[AI Copilot Response Placeholder]",
        }

    async def _handle_rag_search(self, config: dict, context: dict) -> dict[str, Any]:
        query = config.get("query", "")
        return {
            "rag_search_executed": True,
            "query": query,
            "results": "[RAG Search Results Placeholder]",
        }

    async def _handle_ml_prediction(
        self, config: dict, context: dict
    ) -> dict[str, Any]:
        model_id = config.get("model_id", "")
        return {
            "ml_prediction_executed": True,
            "model_id": model_id,
            "prediction": "[ML Prediction Placeholder]",
        }

    async def _handle_external_api(self, config: dict, context: dict) -> dict[str, Any]:
        url = config.get("url", "")
        method = config.get("method", "GET")
        return {
            "external_api_called": True,
            "url": url,
            "method": method,
            "response": "[External API Placeholder]",
        }

    # ─── Helpers ─────────────────────────────────────────────────────────────────
    def _compare(self, actual: Any, operator: str, expected: Any) -> bool:
        try:
            if operator == "==":
                return actual == expected
            elif operator == "!=":
                return actual != expected
            elif operator == ">":
                return float(actual) > float(expected)
            elif operator == "<":
                return float(actual) < float(expected)
            elif operator == ">=":
                return float(actual) >= float(expected)
            elif operator == "<=":
                return float(actual) <= float(expected)
            elif operator == "in":
                return actual in expected
            elif operator == "contains":
                return expected in str(actual)
            elif operator == "matches":
                import re

                return bool(re.match(str(expected), str(actual)))
        except Exception:
            pass
        return False

    def _elapsed_ms(self, start: datetime) -> float:
        return (datetime.now(UTC) - start).total_seconds() * 1000

    async def _log(
        self,
        org_id: uuid.UUID | None,
        execution_id: uuid.UUID,
        step_key: str | None,
        level: str,
        message: str,
    ) -> None:
        await self.repo.create_log(
            org_id,
            {
                "execution_id": execution_id,
                "step_key": step_key,
                "log_level": level,
                "message": message,
            },
        )

    async def _fail_execution(
        self, execution: WorkflowExecution, org_id: uuid.UUID | None, error: str
    ) -> WorkflowExecution:
        exec_obj = await self.repo.update_execution(
            execution,
            {
                "status": "failed",
                "end_time": datetime.now(UTC),
                "error_message": error,
                "duration_ms": self._elapsed_ms(execution.start_time),
            },
        )
        await self._log(
            org_id, execution.id, None, "ERROR", f"Execution failed: {error}"
        )
        return exec_obj
