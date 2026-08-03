from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai_rag_copilot,
    attendance,
    audit,
    auth,
    branches,
    business_unit,
    calendar,
    cost_center,
    crm_sales,
    data_analytics_mlops,
    department,
    designation,
    employee,
    finance_accounting,
    health,
    integration_observability,
    inventory_procurement,
    manufacturing_mrp,
    leave,
    locations,
    mfa,
    office_location,
    organization,
    payroll,
    permission,
    performance_learning,
    recruitment,
    reporting_structure,
    role,
    scheduler,
    sessions,
    team,
    team_members,
    training,
    user,
    version,
)

api_router = APIRouter()

# Core System
api_router.include_router(health.router, prefix="/health", tags=["system"])
api_router.include_router(version.router, prefix="/version", tags=["system"])

# Phase 1 Core Foundation
api_router.include_router(
    organization.router, prefix="/organizations", tags=["organizations"]
)
api_router.include_router(
    calendar.router, prefix="/business-calendar", tags=["calendar"]
)
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_router.include_router(branches.router, prefix="/branches", tags=["branches"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(scheduler.router, prefix="/scheduler", tags=["scheduler"])

# Phase 2 Enterprise Identity Platform
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(role.router, prefix="/roles", tags=["roles"])
api_router.include_router(
    permission.router, prefix="/permissions", tags=["permissions"]
)
api_router.include_router(mfa.router, prefix="/mfa", tags=["mfa"])

# Phase 3 Enterprise Organization Structure Platform
api_router.include_router(
    department.router, prefix="/departments", tags=["departments"]
)
api_router.include_router(
    designation.router, prefix="/designations", tags=["designations"]
)
api_router.include_router(
    business_unit.router, prefix="/business-units", tags=["business-units"]
)
api_router.include_router(team.router, prefix="/teams", tags=["teams"])
api_router.include_router(
    team_members.router, prefix="/team-members", tags=["team-members"]
)
api_router.include_router(
    cost_center.router, prefix="/cost-centers", tags=["cost-centers"]
)
api_router.include_router(
    reporting_structure.router,
    prefix="/reporting-structure",
    tags=["reporting-structure"],
)
api_router.include_router(
    office_location.router, prefix="/office-locations", tags=["office-locations"]
)

# Phase 4 Enterprise Human Resources Platform
api_router.include_router(employee.router, prefix="", tags=["employees"])

# Phase 5 Enterprise Attendance & Time Management Platform
api_router.include_router(attendance.router, prefix="", tags=["attendance"])

# Phase 6 Enterprise Leave & Absence Management Platform
api_router.include_router(leave.router, prefix="", tags=["leave"])

# Phase 7 Enterprise Payroll & Compensation Platform
api_router.include_router(payroll.router, prefix="", tags=["payroll"])

# Phase 8 Enterprise Recruitment & Talent Acquisition Platform
api_router.include_router(recruitment.router, prefix="", tags=["recruitment"])

# Phase 9 Enterprise Performance & Learning Management Platform
api_router.include_router(performance_learning.router, prefix="", tags=["performance_learning"])

# Phase 10 Enterprise CRM & Sales Platform
api_router.include_router(crm_sales.router, prefix="", tags=["crm_sales"])

# Phase 11 Enterprise Inventory, Procurement & Warehouse Management Platform
api_router.include_router(inventory_procurement.router, prefix="", tags=["inventory_procurement"])

# Phase 12 Enterprise Finance & Accounting Platform
api_router.include_router(finance_accounting.router, prefix="", tags=["finance_accounting"])

# Phase 13 Enterprise Manufacturing & MRP Platform
api_router.include_router(manufacturing_mrp.router, prefix="", tags=["manufacturing_mrp"])

# Phase 14 Enterprise AI, RAG & Copilot Platform
api_router.include_router(ai_rag_copilot.router, prefix="", tags=["ai_rag_copilot"])

# Phase 15 Enterprise Data Engineering, Analytics & MLOps Platform
api_router.include_router(data_analytics_mlops.router, prefix="", tags=["data_analytics_mlops"])

# Phase 16 Enterprise Integration, Observability & Production Platform
api_router.include_router(integration_observability.router, prefix="", tags=["integration_observability"])
