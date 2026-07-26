import re
import logging
from typing import List, Dict, Any, Optional
from jinja2 import Template
import uuid

logger = logging.getLogger(__name__)


# ==================== PII DATA MASKING ====================
class PIIMasker:
    # Regex patterns for sensitive PII data
    SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
    CREDIT_CARD_PATTERN = re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b")
    PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b")
    SALARY_PATTERN = re.compile(r"\b(?:salary|wage|compensation|earn|paid)\s*(?:of|is|equals)?\s*(?:\$?\s*\d+(?:,\d{3})*(?:\.\d{2})?)\b", re.IGNORECASE)

    @classmethod
    def mask(cls, text: str, user_roles: List[str]) -> str:
        """
        Mask sensitive data fields from response/prompts if user doesn't have privileges.
        """
        # If user is Admin or HR Manager, we bypass standard masking
        bypass_roles = {"Super Admin", "Admin", "HR Manager", "Finance Manager"}
        if any(r in bypass_roles for r in user_roles):
            return text

        masked = text
        # Mask SSN
        masked = cls.SSN_PATTERN.sub("[SSN MASKED]", masked)
        
        # Mask Credit Cards
        masked = cls.CREDIT_CARD_PATTERN.sub("[CARD MASKED]", masked)
        
        # Mask Emails
        masked = cls.EMAIL_PATTERN.sub("[EMAIL MASKED]", masked)
        
        # Mask Phones
        masked = cls.PHONE_PATTERN.sub("[PHONE MASKED]", masked)
        
        # Mask Salary specifics
        def salary_replacer(match):
            # Capture the match but mask the actual number part
            matched_str = match.group(0)
            # Find any dollar signs and digits
            num_part = re.search(r"\d+(?:,\d{3})*(?:\.\d{2})?", matched_str)
            if num_part:
                return matched_str.replace(num_part.group(0), "[CONFIDENTIAL]")
            return "[SALARY MASKED]"
            
        masked = cls.SALARY_PATTERN.sub(salary_replacer, masked)

        return masked


# ==================== DEFAULT PROMPT TEMPLATES ====================
DEFAULT_SYSTEM_PROMPTS = {
    "generic": (
        "You are the VertexERP AI Copilot, a helpful enterprise assistant. "
        "You are assisting {{ user_name }} from organization '{{ org_name }}' (Tenant ID: {{ org_id }}). "
        "Provide factual, professional answers regarding company operations. "
        "Ensure all financial records, employee directories, and inventory statuses are handled with care. "
        "If you use tool outputs, format them clearly in Markdown tables."
    ),
    "hr": (
        "You are the VertexERP HR Intelligence Assistant. You support employee onboarding, time tracking, "
        "PTO requests, performance reviews, and training courses. "
        "Ensure compliance with payroll structures and maintain strict personnel confidentiality. "
        "User context: {{ user_name }}, Dept: HR."
    ),
    "crm": (
        "You are the VertexERP CRM Intelligence Assistant. You support client management, deals, sales pipeline, "
        "support tickets, and campaign analytics. "
        "Help the team maximize conversions and suggest next-action tasks for cold or stale leads. "
        "User context: {{ user_name }}, Dept: Sales & CRM."
    ),
    "finance": (
        "You are the VertexERP Finance & Accounting Assistant. You support accounts charts, ledger entries, "
        "invoice items, expense claims, tax profiles, and budget limits. "
        "Always double-check currency calculations and format numbers with correct decimal markers. "
        "User context: {{ user_name }}, Dept: Finance."
    ),
    "inventory": (
        "You are the VertexERP Inventory & Warehouse Intelligence Assistant. You support product catalogs, "
        "stock movement logs, transfers, and warehouse bins. "
        "Help maintain optimal safety stock counts and flag items below reorder thresholds. "
        "User context: {{ user_name }}, Dept: Inventory."
    ),
    "manufacturing": (
        "You are the VertexERP Manufacturing & Production Assistant. You support Bill of Materials (BOM), "
        "routings, work center tasks, machines capacity, quality checks, and MRP runs. "
        "Optimize scheduling to minimize downtime and highlight active warnings on the factory floor. "
        "User context: {{ user_name }}, Dept: Operations."
    ),
    "executive": (
        "You are the VertexERP Executive Assistant. You specialize in executive dashboards, KPIs, business performance, "
        "forecast evaluations, and analytical reports. "
        "Provide concise, high-level summaries for leadership decisions. "
        "User context: {{ user_name }} (Executive profile)."
    )
}


class PromptManager:
    @staticmethod
    def render_template(template_str: str, variables: Dict[str, Any]) -> str:
        """
        Render dynamic variables in templates using Jinja2 style.
        """
        try:
            t = Template(template_str)
            return t.render(**variables)
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            # Simple fallback replacement
            rendered = template_str
            for k, v in variables.items():
                rendered = rendered.replace(f"{{{{ {k} }}}}", str(v)).replace(f"{{{{{k}}}}}", str(v))
            return rendered

    @staticmethod
    def get_default_prompt(department: Optional[str] = None) -> str:
        dep_key = (department or "generic").lower()
        return DEFAULT_SYSTEM_PROMPTS.get(dep_key, DEFAULT_SYSTEM_PROMPTS["generic"])


# ==================== CONVERSATION & MEMORY COMPILER ====================
class ContextManager:
    @staticmethod
    def compile_history(
        system_prompt: str,
        chat_history: List[Dict[str, Any]],
        max_messages: int = 15
    ) -> List[Dict[str, str]]:
        """
        Assemble history context including System instruction and sliding session window.
        Returns message payloads ready for LLM consumption.
        """
        compiled = [{"role": "system", "content": system_prompt}]
        
        # Include recent sliding history context
        recent = chat_history[-max_messages:] if chat_history else []
        for msg in recent:
            compiled.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
            
        return compiled


# ==================== REDIS RATE LIMITER ====================
class RedisRateLimiter:
    @staticmethod
    async def is_rate_limited(
        redis_service: Any,
        user_id: uuid.UUID,
        limit: int = 20,
        window_seconds: int = 60
    ) -> bool:
        """
        Verify if user has triggered chat rate limit using Redis token bucket / counters.
        """
        if not redis_service:
            # Bypass rate limit check if Redis client unavailable
            return False
            
        key = f"rate_limit:copilot:{user_id}"
        try:
            # We fetch current client connection
            conn = redis_service.client
            current = await conn.get(key)
            
            if current is not None:
                count = int(current)
                if count >= limit:
                    return True
                await conn.incr(key)
            else:
                # Create key with window expiry
                await conn.set(key, 1, ex=window_seconds)
            return False
        except Exception as e:
            logger.warning(f"Redis rate limiting query failure: {e}")
            return False
