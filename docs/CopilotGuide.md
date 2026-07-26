# Enterprise AI Copilot Platform User Guide

Welcome to the **VertexERP AI Copilot Platform**. This guide covers the features, conversation interface, multi-tenant session isolation boundary, and performance monitoring properties of the Copilot.

---

## 🏛️ System Features

The AI Copilot Platform offers natural language conversation interfaces, automated ERP tool chaining, and context-aware responses tailored to various operational departments.

Key features include:
1. **Natural Language Assistant**: Contextual conversation threads.
2. **Context Manager (Session Scoped)**: Memory manager that compiles the sliding window history for LLM provider consumption.
3. **Pluggable Tool Registry**: Active backend API hooks connecting with CRM, HR, Finance, Inventory, and Manufacturing operations.
4. **Sensitive Data Masking (PII)**: Automatically scans and masks sensitive attributes (SSN, credit card details, salary figures, phone numbers, emails) if the user's role does not allow viewing PII.
5. **Redis Rate Limiting**: Limit check counter protecting service gateways from overload (default: 60 queries/min).

---

## 💻 Conversation Dashboard (UI)

The UI is divided into two panels:
- **Left Panel (Threads list)**: Shows current conversation history threads. Features search filters, session deletion, and pinning. Underneath is the configuration console for LLM provider, default temperature, and department context mapping.
- **Right Panel (Conversation Feed)**: Renders user prompts, assistant answers, citation source panels, feedback buttons, and detailed logs of executed tool parameters.

---

## 🔒 Multi-Tenant Data Isolation

The platform enforces strict tenant boundaries at the database and application levels:
- **Isolation Checks**: All queries (sessions, message logs, metadata) validate and filter by the current authenticated user's `organization_id`.
- **RBAC Checking**: Before executing registered tools, the system matches the user's roles against the tool's `required_role` attribute. If missing, the tool execution is skipped, and the LLM synthesizes a safe fallback explaining the permission boundary.
- **Audit Trails**: Every conversational chat action logs standard operational parameters (tokens, executed tools, latency) inside the DB audit tracking tables.
