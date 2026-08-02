from fastapi import APIRouter

from app.api.v1.endpoints import (
    analytics,
    approvals,
    attendance,
    audit,
    auth,
    branches,
    business_units,
    calendar,
    cloud_costs,
    # Phase 20 – Enterprise Cloud Deployment & Global Release
    cloud_deployments,
    cloud_incidents,
    cloud_regions,
    cloud_releases,
    cloud_status,
    copilot,
    crm_activities,
    crm_campaigns,
    crm_contacts,
    crm_customers,
    crm_deals,
    crm_leads,
    crm_tickets,
    data_engineering,
    departments,
    designations,
    documents,
    employees,
    executions,
    finance,
    health,
    integration_analytics,
    integration_auth,
    # Phase 18 – Enterprise Integration Platform
    integration_connectors,
    integration_events,
    integration_gateway,
    integration_queues,
    integration_webhooks,
    inventory_adjustments,
    inventory_categories,
    inventory_counts,
    inventory_products,
    inventory_purchase,
    inventory_suppliers,
    inventory_transfers,
    inventory_warehouses,
    leaves,
    locations,
    manufacturing,
    ml,
    ml_studio,
    mlops,
    observability,
    organization,
    payroll,
    performance,
    permission,
    production_backups,
    production_compliance,
    production_performance,
    production_readiness,
    production_recovery,
    # Phase 19 – Production Readiness, Performance & Security Hardening
    production_security,
    rag,
    recruitment,
    reporting,
    role,
    rules,
    scheduler,
    teams,
    templates,
    training,
    user,
    version,
    # Phase 17 – Enterprise Workflow Automation
    workflows,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["system"])
api_router.include_router(version.router, prefix="/version", tags=["system"])
api_router.include_router(
    observability.router, prefix="/observability", tags=["observability"]
)

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    organization.router, prefix="/organizations", tags=["organizations"]
)
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(role.router, prefix="/roles", tags=["roles"])
api_router.include_router(
    permission.router, prefix="/permissions", tags=["permissions"]
)
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(branches.router, prefix="/branches", tags=["branches"])
api_router.include_router(
    departments.router, prefix="/departments", tags=["departments"]
)
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(
    designations.router, prefix="/designations", tags=["designations"]
)
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_router.include_router(
    business_units.router, prefix="/business-units", tags=["business-units"]
)
api_router.include_router(
    calendar.router, prefix="/business-calendar", tags=["calendar"]
)
api_router.include_router(
    reporting.router, prefix="/reporting-structure", tags=["reporting"]
)
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(employees.router, prefix="/employees", tags=["hr"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["hr"])
api_router.include_router(leaves.router, prefix="/leaves", tags=["hr"])
api_router.include_router(recruitment.router, prefix="/recruitment", tags=["hr"])
api_router.include_router(performance.router, prefix="/performance", tags=["hr"])
api_router.include_router(training.router, prefix="/training", tags=["hr"])
api_router.include_router(payroll.router, prefix="/payroll", tags=["hr"])
api_router.include_router(crm_leads.router, prefix="/crm/leads", tags=["crm"])
api_router.include_router(crm_customers.router, prefix="/crm/customers", tags=["crm"])
api_router.include_router(crm_contacts.router, prefix="/crm/contacts", tags=["crm"])
api_router.include_router(crm_deals.router, prefix="/crm/deals", tags=["crm"])
api_router.include_router(crm_activities.router, prefix="/crm/activities", tags=["crm"])
api_router.include_router(
    crm_tickets.router, prefix="/crm/support-tickets", tags=["crm"]
)
api_router.include_router(crm_campaigns.router, prefix="/crm/campaigns", tags=["crm"])
api_router.include_router(
    inventory_products.router, prefix="/inventory/products", tags=["inventory"]
)
api_router.include_router(
    inventory_categories.router, prefix="/inventory/categories", tags=["inventory"]
)
api_router.include_router(
    inventory_warehouses.router, prefix="/inventory/warehouses", tags=["inventory"]
)
api_router.include_router(
    inventory_suppliers.router, prefix="/inventory/suppliers", tags=["inventory"]
)
api_router.include_router(
    inventory_purchase.router, prefix="/inventory/purchase-orders", tags=["inventory"]
)
api_router.include_router(
    inventory_transfers.router, prefix="/inventory/transfers", tags=["inventory"]
)
api_router.include_router(
    inventory_adjustments.router, prefix="/inventory/adjustments", tags=["inventory"]
)
api_router.include_router(
    inventory_counts.router, prefix="/inventory/counts", tags=["inventory"]
)
api_router.include_router(finance.router, prefix="/finance", tags=["finance"])
api_router.include_router(
    manufacturing.router, prefix="/manufacturing", tags=["manufacturing"]
)
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(
    data_engineering.router, prefix="/data-engineering", tags=["data-engineering"]
)
api_router.include_router(ml.router, prefix="/ml", tags=["machine-learning"])
api_router.include_router(ml_studio.router, prefix="/ml-studio", tags=["ml-studio"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(copilot.router, prefix="/copilot", tags=["copilot"])
api_router.include_router(mlops.router, prefix="/mlops", tags=["mlops"])

# Phase 17 – Enterprise Workflow Automation Platform
api_router.include_router(
    workflows.router, prefix="/workflows", tags=["workflow-automation"]
)
api_router.include_router(
    rules.router, prefix="/workflow-rules", tags=["workflow-automation"]
)
api_router.include_router(
    executions.router, prefix="/workflow-executions", tags=["workflow-automation"]
)
api_router.include_router(
    approvals.router, prefix="/approvals", tags=["workflow-automation"]
)
api_router.include_router(
    scheduler.router, prefix="/scheduler", tags=["workflow-automation"]
)
api_router.include_router(
    templates.router, prefix="/workflow-templates", tags=["workflow-automation"]
)

# Phase 18 – Enterprise Integration Platform
api_router.include_router(
    integration_connectors.router,
    prefix="/integration/connectors",
    tags=["integration-platform"],
)
api_router.include_router(
    integration_gateway.router,
    prefix="/integration/gateway",
    tags=["integration-platform"],
)
api_router.include_router(
    integration_webhooks.router,
    prefix="/integration/webhooks",
    tags=["integration-platform"],
)
api_router.include_router(
    integration_events.router,
    prefix="/integration/events",
    tags=["integration-platform"],
)
api_router.include_router(
    integration_queues.router,
    prefix="/integration/queues",
    tags=["integration-platform"],
)
api_router.include_router(
    integration_auth.router, prefix="/integration/auth", tags=["integration-platform"]
)
api_router.include_router(
    integration_analytics.router,
    prefix="/integration/analytics",
    tags=["integration-platform"],
)

# Phase 19 – Production Readiness, Performance & Security Hardening
api_router.include_router(
    production_security.router,
    prefix="/production/security",
    tags=["production-readiness"],
)
api_router.include_router(
    production_performance.router,
    prefix="/production/performance",
    tags=["production-readiness"],
)
api_router.include_router(
    production_compliance.router,
    prefix="/production/compliance",
    tags=["production-readiness"],
)
api_router.include_router(
    production_backups.router,
    prefix="/production/backups",
    tags=["production-readiness"],
)
api_router.include_router(
    production_recovery.router,
    prefix="/production/recovery",
    tags=["production-readiness"],
)
api_router.include_router(
    production_readiness.router,
    prefix="/production/readiness",
    tags=["production-readiness"],
)

# Phase 20 – Enterprise Cloud Deployment & Global Release
api_router.include_router(
    cloud_deployments.router, prefix="/cloud/deployments", tags=["cloud-release"]
)
api_router.include_router(
    cloud_releases.router, prefix="/cloud/releases", tags=["cloud-release"]
)
api_router.include_router(
    cloud_regions.router, prefix="/cloud/regions", tags=["cloud-release"]
)
api_router.include_router(
    cloud_incidents.router, prefix="/cloud/incidents", tags=["cloud-release"]
)
api_router.include_router(
    cloud_costs.router, prefix="/cloud/costs", tags=["cloud-release"]
)
api_router.include_router(
    cloud_status.router, prefix="/cloud/status", tags=["cloud-release"]
)
