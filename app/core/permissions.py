"""Standard fine-grained permission codes registry."""

from enum import StrEnum


class PermissionCode(StrEnum):
    """System-wide permission codes formatted as domain:resource:action."""

    # Identity & User Management
    IDENTITY_USERS_READ = "identity:users:read"
    IDENTITY_USERS_CREATE = "identity:users:create"
    IDENTITY_USERS_UPDATE = "identity:users:update"
    IDENTITY_USERS_DELETE = "identity:users:delete"

    # Roles & Permissions
    IDENTITY_ROLES_READ = "identity:roles:read"
    IDENTITY_ROLES_CREATE = "identity:roles:create"
    IDENTITY_ROLES_UPDATE = "identity:roles:update"
    IDENTITY_ROLES_DELETE = "identity:roles:delete"
    IDENTITY_ROLES_ASSIGN = "identity:roles:assign"

    # Organization & Hierarchy
    ORGANIZATION_READ = "organization:organizations:read"
    ORGANIZATION_CREATE = "organization:organizations:create"
    ORGANIZATION_UPDATE = "organization:organizations:update"
    ORGANIZATION_DELETE = "organization:organizations:delete"
    ORGANIZATION_MEMBERS_MANAGE = "organization:members:manage"

    ORGANIZATION_BRANCHES_READ = "organization:branches:read"
    ORGANIZATION_BRANCHES_WRITE = "organization:branches:write"
    ORGANIZATION_BRANCHES_MANAGE = "organization:branches:manage"

    ORGANIZATION_DEPARTMENTS_READ = "organization:departments:read"
    ORGANIZATION_DEPARTMENTS_WRITE = "organization:departments:write"

    ORGANIZATION_TEAMS_READ = "organization:teams:read"
    ORGANIZATION_TEAMS_WRITE = "organization:teams:write"

    ORGANIZATION_DESIGNATIONS_READ = "organization:designations:read"
    ORGANIZATION_DESIGNATIONS_WRITE = "organization:designations:write"

    ORGANIZATION_BUSINESS_UNITS_READ = "organization:business_units:read"
    ORGANIZATION_BUSINESS_UNITS_WRITE = "organization:business_units:write"

    ORGANIZATION_COST_CENTERS_READ = "organization:cost_centers:read"
    ORGANIZATION_COST_CENTERS_WRITE = "organization:cost_centers:write"

    ORGANIZATION_LOCATIONS_READ = "organization:locations:read"
    ORGANIZATION_LOCATIONS_WRITE = "organization:locations:write"

    ORGANIZATION_CALENDARS_READ = "organization:calendars:read"
    ORGANIZATION_CALENDARS_WRITE = "organization:calendars:write"

    ORGANIZATION_HOLIDAYS_READ = "organization:holidays:read"
    ORGANIZATION_HOLIDAYS_WRITE = "organization:holidays:write"

    # Audit & Compliance
    AUDIT_LOGS_READ = "audit:logs:read"
    AUDIT_SECURITY_EVENTS_READ = "audit:security_events:read"

    # Human Resources (HR) Domain
    HR_EMPLOYEES_READ = "hr:employees:read"
    HR_EMPLOYEES_WRITE = "hr:employees:write"
    HR_EMPLOYEES_DELETE = "hr:employees:delete"

    HR_PROFILES_READ = "hr:profiles:read"
    HR_PROFILES_WRITE = "hr:profiles:write"
    HR_PROFILES_SENSITIVE_READ = "hr:profiles:sensitive_read"

    HR_LIFECYCLE_READ = "hr:lifecycle:read"
    HR_LIFECYCLE_WRITE = "hr:lifecycle:write"

    HR_ATTENDANCE_READ = "hr:attendance:read"
    HR_ATTENDANCE_WRITE = "hr:attendance:write"
    HR_ATTENDANCE_APPROVE = "hr:attendance:approve"

    HR_LEAVES_READ = "hr:leaves:read"
    HR_LEAVES_WRITE = "hr:leaves:write"
    HR_LEAVES_APPROVE = "hr:leaves:approve"

    HR_PAYROLL_READ = "hr:payroll:read"
    HR_PAYROLL_WRITE = "hr:payroll:write"
    HR_PAYROLL_PROCESS = "hr:payroll:process"
    HR_PAYROLL_APPROVE = "hr:payroll:approve"
    HR_PAYROLL_DISBURSE = "hr:payroll:disburse"

    HR_RECRUITMENT_READ = "hr:recruitment:read"
    HR_RECRUITMENT_WRITE = "hr:recruitment:write"

    HR_PERFORMANCE_READ = "hr:performance:read"
    HR_PERFORMANCE_WRITE = "hr:performance:write"

    HR_LEARNING_READ = "hr:learning:read"
    HR_LEARNING_WRITE = "hr:learning:write"

    # Customer Relationship Management (CRM) Domain
    CRM_LEADS_READ = "crm:leads:read"
    CRM_LEADS_WRITE = "crm:leads:write"
    CRM_LEADS_DELETE = "crm:leads:delete"
    CRM_LEADS_CONVERT = "crm:leads:convert"

    CRM_CUSTOMERS_READ = "crm:customers:read"
    CRM_CUSTOMERS_WRITE = "crm:customers:write"
    CRM_CUSTOMERS_DELETE = "crm:customers:delete"

    CRM_CONTACTS_READ = "crm:contacts:read"
    CRM_CONTACTS_WRITE = "crm:contacts:write"
    CRM_CONTACTS_DELETE = "crm:contacts:delete"

    CRM_DEALS_READ = "crm:deals:read"
    CRM_DEALS_WRITE = "crm:deals:write"
    CRM_DEALS_DELETE = "crm:deals:delete"
    CRM_PIPELINES_MANAGE = "crm:pipelines:manage"

    CRM_QUOTATIONS_READ = "crm:quotations:read"
    CRM_QUOTATIONS_WRITE = "crm:quotations:write"
    CRM_QUOTATIONS_DELETE = "crm:quotations:delete"
    CRM_QUOTATIONS_CONVERT = "crm:quotations:convert"

    CRM_ORDERS_READ = "crm:orders:read"
    CRM_ORDERS_WRITE = "crm:orders:write"
    CRM_ORDERS_DELETE = "crm:orders:delete"

    CRM_ACTIVITIES_READ = "crm:activities:read"
    CRM_ACTIVITIES_WRITE = "crm:activities:write"
    CRM_ACTIVITIES_DELETE = "crm:activities:delete"

    # Inventory Domain
    INVENTORY_PRODUCTS_READ = "inventory:products:read"
    INVENTORY_PRODUCTS_WRITE = "inventory:products:write"
    INVENTORY_PRODUCTS_DELETE = "inventory:products:delete"

    INVENTORY_UOM_MANAGE = "inventory:uom:manage"

    INVENTORY_WAREHOUSES_READ = "inventory:warehouses:read"
    INVENTORY_WAREHOUSES_WRITE = "inventory:warehouses:write"
    INVENTORY_LOCATIONS_MANAGE = "inventory:locations:manage"

    INVENTORY_RECEIPTS_READ = "inventory:receipts:read"
    INVENTORY_RECEIPTS_WRITE = "inventory:receipts:write"
    INVENTORY_RECEIPTS_POST = "inventory:receipts:post"

    INVENTORY_MOVEMENTS_READ = "inventory:movements:read"

    INVENTORY_TRANSFERS_READ = "inventory:transfers:read"
    INVENTORY_TRANSFERS_WRITE = "inventory:transfers:write"
    INVENTORY_TRANSFERS_EXECUTE = "inventory:transfers:execute"

    INVENTORY_ADJUSTMENTS_READ = "inventory:adjustments:read"
    INVENTORY_ADJUSTMENTS_WRITE = "inventory:adjustments:write"
    INVENTORY_ADJUSTMENTS_APPROVE = "inventory:adjustments:approve"
    INVENTORY_ADJUSTMENTS_POST = "inventory:adjustments:post"

    # Procurement Domain
    PROCUREMENT_SUPPLIERS_READ = "procurement:suppliers:read"
    PROCUREMENT_SUPPLIERS_WRITE = "procurement:suppliers:write"
    PROCUREMENT_SUPPLIERS_DELETE = "procurement:suppliers:delete"

    PROCUREMENT_REQUESTS_READ = "procurement:requests:read"
    PROCUREMENT_REQUESTS_WRITE = "procurement:requests:write"
    PROCUREMENT_REQUESTS_APPROVE = "procurement:requests:approve"

    PROCUREMENT_ORDERS_READ = "procurement:orders:read"
    PROCUREMENT_ORDERS_WRITE = "procurement:orders:write"
    PROCUREMENT_ORDERS_APPROVE = "procurement:orders:approve"
    PROCUREMENT_ORDERS_SEND = "procurement:orders:send"

    # Finance & Accounting Domain
    FINANCE_ACCOUNTS_READ = "finance:accounts:read"
    FINANCE_ACCOUNTS_WRITE = "finance:accounts:write"
    FINANCE_ACCOUNTS_DELETE = "finance:accounts:delete"

    FINANCE_PERIODS_READ = "finance:periods:read"
    FINANCE_PERIODS_MANAGE = "finance:periods:manage"
    FINANCE_PERIODS_LOCK = "finance:periods:lock"

    FINANCE_JOURNALS_READ = "finance:journals:read"
    FINANCE_JOURNALS_WRITE = "finance:journals:write"
    FINANCE_JOURNALS_POST = "finance:journals:post"
    FINANCE_JOURNALS_REVERSE = "finance:journals:reverse"

    FINANCE_INVOICES_READ = "finance:invoices:read"
    FINANCE_INVOICES_WRITE = "finance:invoices:write"
    FINANCE_INVOICES_POST = "finance:invoices:post"

    FINANCE_BILLS_READ = "finance:bills:read"
    FINANCE_BILLS_WRITE = "finance:bills:write"
    FINANCE_BILLS_POST = "finance:bills:post"

    FINANCE_PAYMENTS_READ = "finance:payments:read"
    FINANCE_PAYMENTS_WRITE = "finance:payments:write"
    FINANCE_PAYMENTS_POST = "finance:payments:post"

    FINANCE_BANKING_READ = "finance:banking:read"
    FINANCE_BANKING_WRITE = "finance:banking:write"
    FINANCE_BANKING_RECONCILE = "finance:banking:reconcile"

    FINANCE_REPORTS_READ = "finance:reports:read"

    # Manufacturing & MRP Domain
    MANUFACTURING_BOM_READ = "manufacturing:bom:read"
    MANUFACTURING_BOM_WRITE = "manufacturing:bom:write"
    MANUFACTURING_BOM_DELETE = "manufacturing:bom:delete"

    MANUFACTURING_WORK_CENTERS_READ = "manufacturing:work_centers:read"
    MANUFACTURING_WORK_CENTERS_WRITE = "manufacturing:work_centers:write"

    MANUFACTURING_ROUTINGS_READ = "manufacturing:routings:read"
    MANUFACTURING_ROUTINGS_WRITE = "manufacturing:routings:write"

    MANUFACTURING_ORDERS_READ = "manufacturing:orders:read"
    MANUFACTURING_ORDERS_WRITE = "manufacturing:orders:write"
    MANUFACTURING_ORDERS_EXECUTE = "manufacturing:orders:execute"

    MANUFACTURING_MRP_RUN = "manufacturing:mrp:run"

    MANUFACTURING_QUALITY_READ = "manufacturing:quality:read"
    MANUFACTURING_QUALITY_WRITE = "manufacturing:quality:write"

    # Analytics & Reporting Domain
    ANALYTICS_DASHBOARDS_READ = "analytics:dashboards:read"
    ANALYTICS_DASHBOARDS_MANAGE = "analytics:dashboards:manage"
    ANALYTICS_KPIS_READ = "analytics:kpis:read"
    ANALYTICS_KPIS_MANAGE = "analytics:kpis:manage"
    ANALYTICS_REPORTS_READ = "analytics:reports:read"
    ANALYTICS_REPORTS_EXPORT = "analytics:reports:export"
    ANALYTICS_FINANCE_READ = "analytics:finance:read"
    ANALYTICS_SALES_READ = "analytics:sales:read"
    ANALYTICS_INVENTORY_READ = "analytics:inventory:read"
    ANALYTICS_MFG_READ = "analytics:manufacturing:read"
    ANALYTICS_HR_READ = "analytics:hr:read"

    # AI Platform & Copilot Domain
    AI_COPILOT_USE = "ai:copilot:use"
    AI_CONVERSATIONS_MANAGE = "ai:conversations:manage"
    AI_TOOLS_EXECUTE = "ai:tools:execute"
    AI_MUTATION_CONFIRM = "ai:mutation:confirm"
    AI_CONFIG_MANAGE = "ai:config:manage"
    AI_USAGE_READ = "ai:usage:read"

    # AI Knowledge & RAG Domain
    AI_RAG_DOCUMENTS_READ = "ai:rag:documents:read"
    AI_RAG_DOCUMENTS_WRITE = "ai:rag:documents:write"
    AI_RAG_DOCUMENTS_DELETE = "ai:rag:documents:delete"
    AI_RAG_QUERY = "ai:rag:query"

    # Background Processing & Jobs Domain
    JOBS_READ = "jobs:jobs:read"
    JOBS_WRITE = "jobs:jobs:write"
    JOBS_CANCEL = "jobs:jobs:cancel"
    JOBS_RETRY = "jobs:jobs:retry"
    JOBS_SCHEDULES_MANAGE = "jobs:schedules:manage"


# System Pre-defined Roles
class SystemRole(StrEnum):
    TENANT_ADMIN = "TenantAdmin"
    ORG_ADMIN = "OrgAdmin"
    EXECUTIVE = "Executive"
    CFO = "ChiefFinancialOfficer"
    SENIOR_ACCOUNTANT = "SeniorAccountant"
    AP_CLERK = "AccountsPayableClerk"
    AR_CLERK = "AccountsReceivableClerk"
    HR_MANAGER = "HRManager"
    PAYROLL_OFFICER = "PayrollOfficer"
    SALES_MANAGER = "SalesManager"
    SALES_REPRESENTATIVE = "SalesRepresentative"
    INVENTORY_MANAGER = "InventoryManager"
    PROCUREMENT_OFFICER = "ProcurementOfficer"
    WAREHOUSE_OPERATOR = "WarehouseOperator"
    PLANT_MANAGER = "PlantManager"
    PRODUCTION_PLANNER = "ProductionPlanner"
    QUALITY_INSPECTOR = "QualityInspector"
    MACHINE_OPERATOR = "MachineOperator"
    BUSINESS_ANALYST = "BusinessAnalyst"
    AUDITOR = "Auditor"
    STANDARD_USER = "StandardUser"
