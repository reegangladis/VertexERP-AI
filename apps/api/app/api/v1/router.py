from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    version,
    auth,
    organization,
    user,
    role,
    permission,
    audit,
    branches,
    departments,
    teams,
    designations,
    locations,
    calendar,
    reporting,
    documents,
    employees,
    attendance,
    leaves,
    recruitment,
    performance,
    training,
    payroll,
    crm_leads,
    crm_customers,
    crm_contacts,
    crm_deals,
    crm_activities,
    crm_tickets,
    crm_campaigns,
    inventory_products,
    inventory_categories,
    inventory_warehouses,
    inventory_suppliers,
    inventory_purchase,
    inventory_transfers,
    inventory_adjustments,
    inventory_counts,
    finance,
    manufacturing,
    analytics,
    data_engineering,
    ml,
    ml_studio,
    rag,
    copilot,
    mlops,
    observability,
    # Phase 17 – Enterprise Workflow Automation
    workflows,
    rules,
    executions,
    approvals,
    scheduler,
    templates,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["system"])
api_router.include_router(version.router, prefix="/version", tags=["system"])
api_router.include_router(observability.router, prefix="/observability", tags=["observability"])

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(organization.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(role.router, prefix="/roles", tags=["roles"])
api_router.include_router(permission.router, prefix="/permissions", tags=["permissions"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(branches.router, prefix="/branches", tags=["branches"])
api_router.include_router(departments.router, prefix="/departments", tags=["departments"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(designations.router, prefix="/designations", tags=["designations"])
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_router.include_router(calendar.router, prefix="/business-calendar", tags=["calendar"])
api_router.include_router(reporting.router, prefix="/reporting-structure", tags=["reporting"])
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
api_router.include_router(crm_tickets.router, prefix="/crm/support-tickets", tags=["crm"])
api_router.include_router(crm_campaigns.router, prefix="/crm/campaigns", tags=["crm"])
api_router.include_router(inventory_products.router, prefix="/inventory/products", tags=["inventory"])
api_router.include_router(inventory_categories.router, prefix="/inventory/categories", tags=["inventory"])
api_router.include_router(inventory_warehouses.router, prefix="/inventory/warehouses", tags=["inventory"])
api_router.include_router(inventory_suppliers.router, prefix="/inventory/suppliers", tags=["inventory"])
api_router.include_router(inventory_purchase.router, prefix="/inventory/purchase-orders", tags=["inventory"])
api_router.include_router(inventory_transfers.router, prefix="/inventory/transfers", tags=["inventory"])
api_router.include_router(inventory_adjustments.router, prefix="/inventory/adjustments", tags=["inventory"])
api_router.include_router(inventory_counts.router, prefix="/inventory/counts", tags=["inventory"])
api_router.include_router(finance.router, prefix="/finance", tags=["finance"])
api_router.include_router(manufacturing.router, prefix="/manufacturing", tags=["manufacturing"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(data_engineering.router, prefix="/data-engineering", tags=["data-engineering"])
api_router.include_router(ml.router, prefix="/ml", tags=["machine-learning"])
api_router.include_router(ml_studio.router, prefix="/ml-studio", tags=["ml-studio"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(copilot.router, prefix="/copilot", tags=["copilot"])
api_router.include_router(mlops.router, prefix="/mlops", tags=["mlops"])

# Phase 17 – Enterprise Workflow Automation Platform
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflow-automation"])
api_router.include_router(rules.router, prefix="/workflow-rules", tags=["workflow-automation"])
api_router.include_router(executions.router, prefix="/workflow-executions", tags=["workflow-automation"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["workflow-automation"])
api_router.include_router(scheduler.router, prefix="/scheduler", tags=["workflow-automation"])
api_router.include_router(templates.router, prefix="/workflow-templates", tags=["workflow-automation"])
