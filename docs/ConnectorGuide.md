# Connector Framework Guide — VertexERP AI

## Overview
The **Connector Framework** provides a pluggable, standard interface (`BaseConnector`) for integrating VertexERP AI with third-party enterprise platforms without single cloud provider dependency.

---

## Supported Pluggable Connectors

| Category | Provider | Connector Class | Primary Actions |
|----------|----------|-----------------|-----------------|
| **ERP** | SAP | `SAPConnector` | `sync_purchase_orders`, `fetch_inventory_levels`, `post_journal_entries` |
| **ERP** | Oracle NetSuite | `NetSuiteConnector` | `sync_ledgers`, `fetch_requisitions` |
| **CRM** | Salesforce | `SalesforceConnector` | `sync_accounts`, `sync_contacts`, `sync_opportunities` |
| **CRM** | HubSpot | `HubSpotConnector` | `sync_leads`, `sync_deals` |
| **Payment** | Stripe | `StripeConnector` | `create_payment_intent`, `refund_charge`, `sync_subscriptions` |
| **Payment** | Razorpay | `RazorpayConnector` | `create_order`, `capture_payment`, `fetch_settlement` |
| **Storage** | AWS S3 | `S3Connector` | `upload_file`, `download_file`, `list_bucket` |
| **Storage** | Azure Blob | `AzureBlobConnector` | `upload_blob`, `download_blob` |
| **Storage** | Google Cloud Storage | `GCSConnector` | `upload_object`, `download_object` |
| **Email** | SendGrid | `SendGridConnector` | `send_email`, `get_stats` |
| **SMS** | Twilio | `TwilioConnector` | `send_sms`, `send_whatsapp` |
| **Messaging** | Slack | `SlackConnector` | `post_message`, `upload_snippet` |
| **Messaging** | MS Teams | `TeamsConnector` | `post_card`, `send_notification` |
| **AI** | OpenAI | `OpenAIConnector` | `generate_chat_completion`, `generate_embedding` |
| **AI** | Google Gemini | `GoogleGeminiConnector` | `generate_content`, `embed_content` |
| **IdP** | Auth0 | `Auth0Connector` | `sync_users`, `revoke_session` |
| **IdP** | Okta | `OktaConnector` | `sync_directory`, `verify_sso` |

---

## Adding a Custom Connector

To implement a new pluggable connector:

```python
from app.services.connector_framework import BaseConnector, ConnectorExecuteResponse

class CustomAppConnector(BaseConnector):
    provider_name = "custom_app"
    category = "custom"

    def test_connection(self) -> bool:
        return True

    def get_supported_actions(self) -> list[str]:
        return ["fetch_data", "push_data"]

    def execute_action(self, action: str, payload: dict) -> ConnectorExecuteResponse:
        return ConnectorExecuteResponse(
            status="success",
            action=action,
            records_affected=1,
            latency_ms=15.0,
            data={"result": "processed"},
        )
```
Then register it with `ConnectorFrameworkRegistry.register_connector("custom_app", CustomAppConnector)`.
