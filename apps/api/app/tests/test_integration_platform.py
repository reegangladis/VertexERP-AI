import pytest
from app.services.secret_manager import SecretManagerService
from app.services.api_gateway import ApiGatewayService
from app.services.connector_framework import ConnectorFrameworkRegistry
from app.services.webhook_engine import WebhookEngine
from app.services.event_bus import EventBus
from app.services.message_queue import MessageQueueService
from app.services.file_integration import FileIntegrationService, S3StorageProvider


# 1. Secret Manager Encryption Tests
def test_secret_manager_encryption():
    mgr = SecretManagerService("test-secret-key-2026")
    raw_credentials = {"api_key": "sk_test_12345", "client_secret": "sec_98765"}
    encrypted = mgr.encrypt_credentials(raw_credentials)

    assert encrypted != str(raw_credentials)
    decrypted = mgr.decrypt_credentials(encrypted)
    assert decrypted == raw_credentials


# 2. API Gateway Service Tests
def test_api_gateway_routing():
    gateway = ApiGatewayService()
    route_res = gateway.route_request("/v1/erp/sync", "GET")
    assert route_res["version"] == "v1"
    assert route_res["target_service"] == "erp_connector"

    v2_res = gateway.route_request("/v2/analytics/reports", "POST")
    assert v2_res["version"] == "v2"


def test_api_gateway_rate_limiting():
    gateway = ApiGatewayService()
    client = "client_test_1"
    # Fill up limit of 5 rps
    for _ in range(5):
        allowed, rem = gateway.check_rate_limit(client, limit_rps=5)
        assert allowed is True

    # 6th request should be blocked
    allowed, rem = gateway.check_rate_limit(client, limit_rps=5)
    assert allowed is False
    assert rem == 0


def test_api_gateway_caching():
    gateway = ApiGatewayService()
    cache_key = "query_invoice_101"
    payload = {"invoice_id": "101", "total": 450.00}

    assert gateway.get_cached_response(cache_key) is None
    gateway.set_cached_response(cache_key, payload, ttl_seconds=10)

    cached_val = gateway.get_cached_response(cache_key)
    assert cached_val == payload


def test_api_gateway_api_key_verification():
    gateway = ApiGatewayService()
    res_valid = gateway.verify_api_key("vx_live_abcdef1234567890")
    assert res_valid.valid is True
    assert "read" in res_valid.scopes

    res_invalid = gateway.verify_api_key("invalid_key")
    assert res_invalid.valid is False


# 3. Connector Framework Tests
def test_connector_framework_registry():
    registry = ConnectorFrameworkRegistry()
    providers = registry.list_available_providers()
    assert len(providers) >= 8

    sap = registry.get_connector("sap")
    assert sap is not None
    assert sap.test_connection() is True

    exec_res = sap.execute_action("sync_purchase_orders", {"po_id": "PO_99123"})
    assert exec_res.status == "success"
    assert exec_res.records_affected == 15


def test_stripe_connector():
    registry = ConnectorFrameworkRegistry()
    stripe = registry.get_connector("stripe")
    assert stripe is not None
    res = stripe.execute_action("create_payment_intent", {"amount": 5000})
    assert res.status == "success"
    assert "stripe_payment_intent_id" in res.data


# 4. Webhook Engine Tests
def test_webhook_hmac_signature():
    engine = WebhookEngine()
    secret = "whsec_test_secret_123"
    payload_str = '{"event":"order.created","amount":100}'
    timestamp = 1774500000

    sig_header = engine.calculate_signature(secret, payload_str, timestamp)
    assert "t=1774500000,v1=" in sig_header


def test_webhook_event_filtering():
    engine = WebhookEngine()
    subscribed = ["order.created", "crm.*"]

    assert engine.matches_event_filter(subscribed, "order.created") is True
    assert engine.matches_event_filter(subscribed, "crm.lead.updated") is True
    assert engine.matches_event_filter(subscribed, "finance.invoice.paid") is False


def test_webhook_exponential_backoff():
    engine = WebhookEngine()
    delay_1 = engine.calculate_exponential_backoff(attempt=1, base_delay=1.0)
    delay_2 = engine.calculate_exponential_backoff(attempt=2, base_delay=1.0)
    delay_3 = engine.calculate_exponential_backoff(attempt=3, base_delay=1.0)

    assert delay_1 == 1.0
    assert delay_2 == 2.0
    assert delay_3 == 4.0


# 5. Event Bus Tests
def test_event_bus_publishing_and_dlq():
    bus = EventBus()
    topic = bus.create_topic("erp.order.created")
    assert topic["name"] == "erp.order.created"

    pub = bus.publish_event("erp.order.created", {"order_id": "ORD_1001"})
    assert pub["status"] == "published"
    assert pub["event_id"].startswith("evt_")


def test_event_bus_replay():
    bus = EventBus()
    bus.publish_event("erp.order.created", {"order_id": "ORD_1001"})
    bus.publish_event("erp.order.created", {"order_id": "ORD_1002"})

    replayed = bus.replay_events("erp.order.created")
    assert len(replayed) == 2
    assert replayed[0]["is_replayed"] is True


# 6. Message Queue Tests
def test_message_queue_lifecycle():
    mq = MessageQueueService()
    enqueued = mq.enqueue_message("inventory_sync_queue", {"product_id": "P-100", "qty": 50})
    assert enqueued["status"] == "pending"

    dequeued = mq.dequeue_message("inventory_sync_queue", "worker_1")
    assert dequeued is not None
    assert dequeued["status"] == "processing"

    acked = mq.ack_message("inventory_sync_queue", dequeued["message_id"])
    assert acked is True


def test_message_queue_nack_to_dlq():
    mq = MessageQueueService()
    enqueued = mq.enqueue_message("test_queue", {"data": "test"}, max_retries=1)

    dequeued = mq.dequeue_message("test_queue", "worker_1")
    mq.nack_message("test_queue", dequeued["message_id"], "Processing exception")

    stats = mq.get_queue_stats()
    test_q_stat = [s for s in stats if s["queue_name"] == "test_queue"][0]
    assert test_q_stat["failed"] == 1


# 7. File Integration Tests
def test_file_parsers():
    svc = FileIntegrationService(S3StorageProvider())

    # CSV
    csv_data = "id,name\n1,Alice\n2,Bob"
    parsed_csv = svc.parse_csv(csv_data)
    assert len(parsed_csv) == 2
    assert parsed_csv[0]["name"] == "Alice"

    # JSON
    json_data = '{"status": "ok", "items": [1, 2, 3]}'
    parsed_json = svc.parse_json(json_data)
    assert parsed_json["status"] == "ok"

    # PDF Metadata
    pdf_meta = svc.extract_pdf_metadata(b"dummy_pdf_bytes_header" * 100)
    assert pdf_meta["format"] == "PDF-1.7"
