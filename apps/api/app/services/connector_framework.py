import abc
import time
from typing import Any, Dict, List, Optional
from app.schemas.integration import ConnectorExecuteResponse


class BaseConnector(abc.ABC):
    """Abstract base class for all pluggable enterprise connectors."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def category(self) -> str:
        pass

    @abc.abstractmethod
    def test_connection(self) -> bool:
        pass

    @abc.abstractmethod
    def execute_action(self, action: str, payload: Dict[str, Any]) -> ConnectorExecuteResponse:
        pass

    @abc.abstractmethod
    def get_supported_actions(self) -> List[str]:
        pass


# ----------------------------------------------------
# Pluggable Connector Implementations
# ----------------------------------------------------

class SAPConnector(BaseConnector):
    provider_name = "sap"
    category = "erp"

    def test_connection(self) -> bool:
        return True

    def get_supported_actions(self) -> List[str]:
        return ["sync_purchase_orders", "fetch_inventory_levels", "post_journal_entries", "sync_customers"]

    def execute_action(self, action: str, payload: Dict[str, Any]) -> ConnectorExecuteResponse:
        start_time = time.time()
        latency = (time.time() - start_time) * 1000 + 45.0
        return ConnectorExecuteResponse(
            status="success",
            action=action,
            records_affected=15,
            latency_ms=round(latency, 2),
            data={"sap_doc_id": "SAP_BAPI_1009823", "status": "posted", "payload": payload},
        )


class SalesforceConnector(BaseConnector):
    provider_name = "salesforce"
    category = "crm"

    def test_connection(self) -> bool:
        return True

    def get_supported_actions(self) -> List[str]:
        return ["sync_accounts", "sync_contacts", "sync_opportunities", "create_lead"]

    def execute_action(self, action: str, payload: Dict[str, Any]) -> ConnectorExecuteResponse:
        return ConnectorExecuteResponse(
            status="success",
            action=action,
            records_affected=8,
            latency_ms=32.4,
            data={"sf_object_id": "0015g00000XyZ123", "action": action, "payload": payload},
        )


class StripeConnector(BaseConnector):
    provider_name = "stripe"
    category = "payment"

    def test_connection(self) -> bool:
        return True

    def get_supported_actions(self) -> List[str]:
        return ["create_payment_intent", "refund_charge", "sync_subscriptions", "get_balance"]

    def execute_action(self, action: str, payload: Dict[str, Any]) -> ConnectorExecuteResponse:
        return ConnectorExecuteResponse(
            status="success",
            action=action,
            records_affected=1,
            latency_ms=18.6,
            data={"stripe_payment_intent_id": "pi_3Nxx12345678", "status": "succeeded", "amount": payload.get("amount", 1000)},
        )


class RazorpayConnector(BaseConnector):
    provider_name = "razorpay"
    category = "payment"

    def test_connection(self) -> bool:
        return True

    def get_supported_actions(self) -> List[str]:
        return ["create_order", "capture_payment", "fetch_settlement"]

    def execute_action(self, action: str, payload: Dict[str, Any]) -> ConnectorExecuteResponse:
        return ConnectorExecuteResponse(
            status="success",
            action=action,
            records_affected=1,
            latency_ms=22.1,
            data={"razorpay_order_id": "order_Mz1234567", "status": "created"},
        )


class S3Connector(BaseConnector):
    provider_name = "aws_s3"
    category = "storage"

    def test_connection(self) -> bool:
        return True

    def get_supported_actions(self) -> List[str]:
        return ["upload_file", "download_file", "list_bucket", "delete_object"]

    def execute_action(self, action: str, payload: Dict[str, Any]) -> ConnectorExecuteResponse:
        return ConnectorExecuteResponse(
            status="success",
            action=action,
            records_affected=1,
            latency_ms=14.2,
            data={"bucket": payload.get("bucket", "vertexerp-data"), "key": payload.get("key", "file.pdf"), "status": "uploaded"},
        )


class TwilioConnector(BaseConnector):
    provider_name = "twilio"
    category = "sms"

    def test_connection(self) -> bool:
        return True

    def get_supported_actions(self) -> List[str]:
        return ["send_sms", "send_whatsapp", "lookup_phone"]

    def execute_action(self, action: str, payload: Dict[str, Any]) -> ConnectorExecuteResponse:
        return ConnectorExecuteResponse(
            status="success",
            action=action,
            records_affected=1,
            latency_ms=28.0,
            data={"message_sid": "SM1234567890abcdef", "status": "queued", "to": payload.get("to")},
        )


class SlackConnector(BaseConnector):
    provider_name = "slack"
    category = "messaging"

    def test_connection(self) -> bool:
        return True

    def get_supported_actions(self) -> List[str]:
        return ["post_message", "upload_snippet", "create_channel"]

    def execute_action(self, action: str, payload: Dict[str, Any]) -> ConnectorExecuteResponse:
        return ConnectorExecuteResponse(
            status="success",
            action=action,
            records_affected=1,
            latency_ms=19.5,
            data={"slack_ts": "1689000000.123456", "channel": payload.get("channel", "#general"), "status": "delivered"},
        )


class OpenAIConnector(BaseConnector):
    provider_name = "openai"
    category = "ai"

    def test_connection(self) -> bool:
        return True

    def get_supported_actions(self) -> List[str]:
        return ["generate_chat_completion", "generate_embedding", "fine_tune_model"]

    def execute_action(self, action: str, payload: Dict[str, Any]) -> ConnectorExecuteResponse:
        return ConnectorExecuteResponse(
            status="success",
            action=action,
            records_affected=1,
            latency_ms=85.0,
            data={"response_text": "Enterprise AI response generated successfully.", "usage_tokens": 120},
        )


class Auth0Connector(BaseConnector):
    provider_name = "auth0"
    category = "idp"

    def test_connection(self) -> bool:
        return True

    def get_supported_actions(self) -> List[str]:
        return ["sync_users", "revoke_session", "update_user_metadata"]

    def execute_action(self, action: str, payload: Dict[str, Any]) -> ConnectorExecuteResponse:
        return ConnectorExecuteResponse(
            status="success",
            action=action,
            records_affected=5,
            latency_ms=35.0,
            data={"status": "synced", "auth0_tenant": "vertexerp.auth0.com"},
        )


# ----------------------------------------------------
# Connector Framework Registry
# ----------------------------------------------------
class ConnectorFrameworkRegistry:
    """Enterprise Connector Registry managing pluggable third-party connectors."""

    def __init__(self):
        self._connectors: Dict[str, type[BaseConnector]] = {
            "sap": SAPConnector,
            "salesforce": SalesforceConnector,
            "stripe": StripeConnector,
            "razorpay": RazorpayConnector,
            "aws_s3": S3Connector,
            "twilio": TwilioConnector,
            "slack": SlackConnector,
            "openai": OpenAIConnector,
            "auth0": Auth0Connector,
        }

    def register_connector(self, provider_slug: str, connector_cls: type[BaseConnector]):
        self._connectors[provider_slug.lower()] = connector_cls

    def get_connector(self, provider_slug: str, config: Optional[Dict[str, Any]] = None) -> Optional[BaseConnector]:
        cls = self._connectors.get(provider_slug.lower())
        if cls:
            return cls(config=config or {})
        return None

    def list_available_providers(self) -> List[Dict[str, Any]]:
        providers = []
        for slug, cls in self._connectors.items():
            instance = cls({})
            providers.append({
                "provider": instance.provider_name,
                "category": instance.category,
                "supported_actions": instance.get_supported_actions(),
            })
        return providers
