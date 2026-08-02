"""
Business Rule Engine — evaluates condition trees against runtime context data.
Supports: ==, !=, >, <, >=, <=, in, contains, matches operators.
Supports: AND / OR logical groups, rule priority ordering, rule group filtering.
"""

import re
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.workflow import RuleEvaluationRequest, RuleEvaluationResult


class RuleEngine:
    """Enterprise business rule evaluator."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = WorkflowRepository(db)

    # ─── Public API ──────────────────────────────────────────────────────────────
    async def evaluate_rules(
        self,
        org_id: uuid.UUID | None,
        request: RuleEvaluationRequest,
    ) -> RuleEvaluationResult:
        """Evaluate all active rules in a group against the provided context data."""
        rules = await self.repo.list_rules(
            org_id, rule_group=request.rule_group, is_active=True
        )

        triggered_actions: list[dict[str, Any]] = []
        matched_rule_ids: list[uuid.UUID] = []

        for rule in sorted(rules, key=lambda r: r.priority):
            matched = self._evaluate_conditions(
                rule.conditions_json, request.context_data
            )
            if matched:
                matched_rule_ids.append(rule.id)
                actions = rule.actions_json.get("actions", [])
                triggered_actions.extend(actions)

        return RuleEvaluationResult(
            evaluated_rules_count=len(rules),
            matched_rules_count=len(matched_rule_ids),
            triggered_actions=triggered_actions,
            matched_rule_ids=matched_rule_ids,
        )

    async def test_rule(
        self,
        rule_id: uuid.UUID,
        org_id: uuid.UUID | None,
        context_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Test a single rule against provided test data."""
        rule = await self.repo.get_rule(org_id, rule_id)
        if not rule:
            return {"error": "Rule not found"}
        matched = self._evaluate_conditions(rule.conditions_json, context_data)
        return {
            "rule_id": str(rule.id),
            "rule_name": rule.name,
            "matched": matched,
            "triggered_actions": (
                rule.actions_json.get("actions", []) if matched else []
            ),
        }

    # ─── Core Evaluator ──────────────────────────────────────────────────────────
    def _evaluate_conditions(
        self, conditions_json: dict[str, Any], context: dict[str, Any]
    ) -> bool:
        """
        Evaluate a conditions tree. Supported structure:
        {
          "logical_operator": "AND" | "OR",
          "conditions": [
            { "field": "amount", "operator": ">=", "value": 1000 },
            ...
          ],
          "groups": [
            { "logical_operator": "OR", "conditions": [...] }
          ]
        }
        """
        logical_op = conditions_json.get("logical_operator", "AND").upper()
        conditions: list[dict] = conditions_json.get("conditions", [])
        groups: list[dict] = conditions_json.get("groups", [])

        results: list[bool] = []
        for cond in conditions:
            results.append(self._eval_single(cond, context))
        for group in groups:
            results.append(self._evaluate_conditions(group, context))

        if not results:
            return True

        if logical_op == "AND":
            return all(results)
        elif logical_op == "OR":
            return any(results)
        return all(results)

    def _eval_single(self, condition: dict[str, Any], context: dict[str, Any]) -> bool:
        field = condition.get("field", "")
        operator = condition.get("operator", "==")
        expected = condition.get("value")
        actual = self._resolve_field(field, context)

        return self._compare(actual, operator, expected)

    def _resolve_field(self, field: str, context: dict[str, Any]) -> Any:
        """Support dot notation: 'order.amount' → context['order']['amount']."""
        parts = field.split(".")
        val: Any = context
        for part in parts:
            if isinstance(val, dict):
                val = val.get(part)
            else:
                return None
        return val

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
                if isinstance(expected, list):
                    return actual in expected
                return str(actual) in str(expected)
            elif operator == "not_in":
                if isinstance(expected, list):
                    return actual not in expected
                return str(actual) not in str(expected)
            elif operator == "contains":
                return str(expected).lower() in str(actual).lower()
            elif operator == "not_contains":
                return str(expected).lower() not in str(actual).lower()
            elif operator == "starts_with":
                return str(actual).lower().startswith(str(expected).lower())
            elif operator == "ends_with":
                return str(actual).lower().endswith(str(expected).lower())
            elif operator == "matches":
                return bool(re.match(str(expected), str(actual)))
            elif operator == "is_null":
                return actual is None
            elif operator == "is_not_null":
                return actual is not None
        except Exception:
            pass
        return False

    def validate_conditions_schema(
        self, conditions_json: dict[str, Any]
    ) -> tuple[bool, str]:
        """Validate that a conditions_json is syntactically valid."""
        if not isinstance(conditions_json, dict):
            return False, "conditions_json must be a dict"
        if "conditions" not in conditions_json and "groups" not in conditions_json:
            return False, "conditions_json must contain 'conditions' or 'groups'"
        for cond in conditions_json.get("conditions", []):
            if not all(k in cond for k in ["field", "operator"]):
                return (
                    False,
                    f"Each condition must have 'field' and 'operator'. Got: {cond}",
                )
            valid_ops = [
                "==",
                "!=",
                ">",
                "<",
                ">=",
                "<=",
                "in",
                "not_in",
                "contains",
                "not_contains",
                "starts_with",
                "ends_with",
                "matches",
                "is_null",
                "is_not_null",
            ]
            if cond["operator"] not in valid_ops:
                return False, f"Unsupported operator: {cond['operator']}"
        return True, "valid"
