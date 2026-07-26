# Prompt Engineering & Template Management Guide

This guide explains how to construct system boundaries, write department templates, and test variable rendering within the **VertexERP AI Copilot Platform**.

---

## 🛠️ Prompt Templates Architecture

Prompts are stored inside the `copilot_prompts` database table, allowing administrators to customize context properties.

### Template Types
1. **System Prompt**: Main operational instructions containing default behavioral guidance for the assistant.
2. **Department Prompt**: Context overrides tailored to specific operational departments:
   - **HR**: Focuses on compliance, time tracking, and training.
   - **CRM**: Focuses on conversions, leads tracking, and tickets support.
   - **Finance**: Enforces decimal precision, accounts calculations, and currency checks.
   - **Inventory**: Enforces stock level limits and reorder thresholds.
   - **Manufacturing**: Optimizes scheduling, routing, and machine operating capacities.

---

## 📐 Template Compilation & Variables

The template compiler utilizes Jinja2 syntax to inject live context dynamically before shipping prompts to LLM providers.

### Standard Variables
- `user_name`: First name or username of the active logged-in employee.
- `org_name`: Organization name linked with the tenant context.
- `org_id`: Tenant UUID string.

### Example Template
```jinja2
You are the VertexERP CRM Intelligence Assistant. You support client management.
Assisting User: {{ user_name }} from company {{ org_name }}.
Always ensure CRM leads are assigned inside the organization sandbox boundary (Tenant: {{ org_id }}).
```

---

## 🧪 Testing Prompts Sandbox

The prompt manager features an interactive sandbox compiler:
1. **Select / Input Template**: Enter your template string (containing `{{ variables }}`).
2. **Setup Mock Variables JSON**: Populate key-values representing active contexts, e.g.:
   ```json
   {
     "user_name": "Sarah Miller",
     "org_name": "Main Logistics Ltd",
     "org_id": "0ee4da49-e236-401f-bdc6-6ac15362a5a6"
   }
   ```
3. **Execute Test Render**: Computes and previews the final rendered prompt block, confirming correct evaluation syntax before publishing the template version.
