# Security Hardening & OWASP Defense Guide — VertexERP AI

## Overview
VertexERP AI enforces a defense-in-depth security model to protect enterprise assets, tenant data, and API endpoints against OWASP Top 10 vulnerabilities.

---

## 1. Content Security Policy (CSP) & HTTP Headers

The `SecurityHeadersMiddleware` injects strict security headers into every HTTP response:

- `Content-Security-Policy`: `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' ...`
- `Strict-Transport-Security`: `max-age=31536000; includeSubDomains; preload`
- `X-Frame-Options`: `DENY`
- `X-Content-Type-Options`: `nosniff`
- `X-XSS-Protection`: `1; mode=block`
- `Referrer-Policy`: `strict-origin-when-cross-origin`
- `Permissions-Policy`: `geolocation=(), microphone=(), camera=()`

---

## 2. OWASP Top 10 Protections

- **SQL Injection (SQLi)**: Parameterized queries via SQLAlchemy ORM combined with regex inspection (`UNION SELECT`, `OR 1=1`, `DROP TABLE`).
- **Cross-Site Scripting (XSS)**: HTML entity escaping via `html.escape()` and script tag stripping.
- **CSRF Protection**: SameSite cookie policies and double-submit token validation.
- **SSRF Protection**: URL whitelist validation blocking loopback IPs (`127.0.0.1`, `localhost`) and cloud metadata endpoints (`169.254.169.254`).
- **Account Lockout**: 5 failed login attempts trigger a 15-minute lock.
- **Password Policy**: Minimum 12 characters, requiring uppercase, lowercase, numbers, and special characters.

---

## 3. Secret Rotation Architecture

System secrets (JWT secrets, Database credentials, Webhook HMAC keys) support automated 90-day rotation cycles with Vault/KMS abstraction interfaces.
