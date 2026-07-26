# Webhook Engine Guide — VertexERP AI

## Overview
The **Webhook Engine** handles secure event dispatching and reception for third-party integrations, featuring cryptographic HMAC signature calculation, topic event filtering, and automatic exponential backoff retries.

---

## Webhook Registration & Headers

Outgoing webhook requests contain standard security headers:

- `X-Webhook-Signature`: `t=<timestamp>,v1=<hmac_sha256_hex_signature>`
- `X-Webhook-Event`: `<event_topic_name>` e.g. `order.created`
- `X-Webhook-Timestamp`: Unix epoch timestamp string

---

## Verifying Incoming Webhook Signatures

To verify an incoming webhook signature:

1. Extract timestamp `t` and signature `v1` from `X-Webhook-Signature`.
2. Compute `expected = HMAC_SHA256(secret, "t.payload_string")`.
3. Compare `expected` and `v1` using constant-time string comparison.

Example Python verification:

```python
from app.services.webhook_engine import WebhookEngine

is_valid = WebhookEngine.verify_signature(
    secret="whsec_1234567890abcdef",
    payload_str='{"event":"order.created"}',
    signature_header="t=1774500000,v1=a1b2c3d4e5f6...",
)
```

---

## Exponential Backoff Retry Policy

Failed webhook deliveries (HTTP status >= 400 or network timeout) trigger exponential retries:

$$\text{Delay}(n) = \min(\text{base} \times 2^{n-1}, \text{max\_delay})$$

- **Attempt 1**: Immediate
- **Attempt 2**: 2 seconds
- **Attempt 3**: 4 seconds
- **Attempt 4**: 8 seconds
- **Attempt 5**: 16 seconds
- **Final**: Routed to Webhook Failure Log
