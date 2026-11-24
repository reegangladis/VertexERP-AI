import React from "react";
import { createBrowserRouter, Navigate } from "react-router-dom";
import { useAuthStore } from "@/stores/auth-store";
import { AppShell } from "@/components/layout/AppShell";
import { ProtectedRoute } from "@/components/security/ProtectedRoute";
import { LoginPage } from "@/features/auth/pages/LoginPage";
import { OrganizationOverviewPage } from "@/features/organization/pages/OrganizationOverviewPage";
import { BranchesPage } from "@/features/organization/pages/BranchesPage";
import { DepartmentsPage } from "@/features/organization/pages/DepartmentsPage";
import { TeamsPage } from "@/features/organization/pages/TeamsPage";
import { DesignationsPage } from "@/features/organization/pages/DesignationsPage";
import { BusinessUnitsPage } from "@/features/organization/pages/BusinessUnitsPage";
import { CostCentersPage } from "@/features/organization/pages/CostCentersPage";
import { LocationsPage } from "@/features/organization/pages/LocationsPage";
import { CalendarsPage } from "@/features/organization/pages/CalendarsPage";
import { HolidaysPage } from "@/features/organization/pages/HolidaysPage";

// HR Administration Pages
import { HROverviewPage } from "@/features/hr/pages/HROverviewPage";
import { EmployeesPage } from "@/features/hr/pages/EmployeesPage";
import { EmployeeProfilePage } from "@/features/hr/pages/EmployeeProfilePage";
import { AttendancePage } from "@/features/hr/pages/AttendancePage";
import { LeaveManagementPage } from "@/features/hr/pages/LeaveManagementPage";
import { PayrollDashboardPage } from "@/features/hr/pages/PayrollDashboardPage";
import { RecruitmentPage } from "@/features/hr/pages/RecruitmentPage";
import { PerformancePage } from "@/features/hr/pages/PerformancePage";
import { LearningPage } from "@/features/hr/pages/LearningPage";

// Employee Self-Service (ESS) Pages
import { ESSHomePage } from "@/features/ess/pages/ESSHomePage";
import { MyAttendancePage } from "@/features/ess/pages/MyAttendancePage";
import { ApplyLeavePage } from "@/features/ess/pages/ApplyLeavePage";
import { MyPayslipsPage } from "@/features/ess/pages/MyPayslipsPage";
import { MyProfilePage } from "@/features/ess/pages/MyProfilePage";
import { MyDocumentsPage } from "@/features/ess/pages/MyDocumentsPage";
import { MyRequestsPage } from "@/features/ess/pages/MyRequestsPage";
import { AnnouncementsPage } from "@/features/ess/pages/AnnouncementsPage";

// CRM & Sales Pages
import { CRMHomePage } from "@/features/crm/pages/CRMHomePage";
import { LeadsPage } from "@/features/crm/pages/LeadsPage";
import { AccountsPage } from "@/features/crm/pages/AccountsPage";
import { ContactsPage } from "@/features/crm/pages/ContactsPage";
import { OpportunitiesPage } from "@/features/crm/pages/OpportunitiesPage";
import { ActivitiesPage } from "@/features/crm/pages/ActivitiesPage";
import { QuotationsPage } from "@/features/crm/pages/QuotationsPage";
import { SalesOrdersPage } from "@/features/crm/pages/SalesOrdersPage";
import { SalesReportsPage } from "@/features/crm/pages/SalesReportsPage";

// Centralized Workflow & Approvals
import { ApprovalsInboxPage } from "@/features/approvals/pages/ApprovalsInboxPage";

// Inventory Pages
import { InventoryOverviewPage } from "@/features/inventory/pages/InventoryOverviewPage";
import { ProductsPage } from "@/features/inventory/pages/ProductsPage";
import { WarehousesPage } from "@/features/inventory/pages/WarehousesPage";
import { StockBalancesPage } from "@/features/inventory/pages/StockBalancesPage";
import { StockLedgerPage } from "@/features/inventory/pages/StockLedgerPage";
import { StockTransfersPage } from "@/features/inventory/pages/StockTransfersPage";
import { StockAdjustmentsPage } from "@/features/inventory/pages/StockAdjustmentsPage";
import { GoodsReceiptsPage } from "@/features/inventory/pages/GoodsReceiptsPage";

// Procurement Pages
import { ProcurementOverviewPage } from "@/features/procurement/pages/ProcurementOverviewPage";
import { SuppliersPage } from "@/features/procurement/pages/SuppliersPage";
import { PurchaseRequestsPage } from "@/features/procurement/pages/PurchaseRequestsPage";
import { PurchaseOrdersPage } from "@/features/procurement/pages/PurchaseOrdersPage";

// Finance & Accounting Pages
import { FinanceOverviewPage } from "@/features/finance/pages/FinanceOverviewPage";
import { ChartOfAccountsPage } from "@/features/finance/pages/ChartOfAccountsPage";
import { FiscalPeriodsPage } from "@/features/finance/pages/FiscalPeriodsPage";
import { JournalEntriesPage } from "@/features/finance/pages/JournalEntriesPage";
import { InvoicesPage } from "@/features/finance/pages/InvoicesPage";
import { BillsPage } from "@/features/finance/pages/BillsPage";
import { PaymentsPage } from "@/features/finance/pages/PaymentsPage";
import { BankAccountsPage } from "@/features/finance/pages/BankAccountsPage";
import { FinancialReportsPage } from "@/features/finance/pages/FinancialReportsPage";

// Manufacturing & MRP Pages
import { ManufacturingOverviewPage } from "@/features/manufacturing/pages/ManufacturingOverviewPage";
import { BillsOfMaterialsPage } from "@/features/manufacturing/pages/BillsOfMaterialsPage";
import { RoutingsPage } from "@/features/manufacturing/pages/RoutingsPage";
import { WorkCentersPage } from "@/features/manufacturing/pages/WorkCentersPage";
import { ProductionOrdersPage } from "@/features/manufacturing/pages/ProductionOrdersPage";
import { WorkOrdersPage } from "@/features/manufacturing/pages/WorkOrdersPage";
import { MaterialConsumptionPage } from "@/features/manufacturing/pages/MaterialConsumptionPage";
import { MRPEnginePage } from "@/features/manufacturing/pages/MRPEnginePage";
import { QualityInspectionsPage } from "@/features/manufacturing/pages/QualityInspectionsPage";

// Analytics & Intelligence Pages
import {
  ExecutiveDashboardPage,
  FinancialAnalyticsPage,
  SalesAnalyticsPage,
  InventoryAnalyticsPage,
  ManufacturingAnalyticsPage,
  HRAnalyticsPage,
  KPICatalogPage,
  ReportsHubPage,
} from "@/features/analytics";

// AI Platform & Copilot Pages
import { AICopilotPage, AIKnowledgeBasePage, AIUsageTelemetryPage } from "@/features/ai";
import { MLPredictivePage } from "@/features/ai/pages/MLPredictivePage";
import { ResumeIntelligencePage } from "@/features/ai/pages/ResumeIntelligencePage";
import { SalesForecastingPage } from "@/features/ai/pages/SalesForecastingPage";

// Background Processing & Jobs Pages
import { BackgroundJobsDashboardPage } from "@/features/jobs";

const RoleHomeRedirect: React.FC = () => {
  const { roles } = useAuthStore();
  if (roles.includes("EMPLOYEE") && !roles.includes("SUPER_ADMIN") && !roles.includes("ORG_ADMIN")) {
    return <Navigate to="/ess/dashboard" replace />;
  }
  if (roles.includes("SALES_MANAGER") && !roles.includes("SUPER_ADMIN")) {
    return <Navigate to="/crm/home" replace />;
  }
  if (roles.includes("HR_MANAGER") && !roles.includes("SUPER_ADMIN")) {
    return <Navigate to="/hr" replace />;
  }
  return <Navigate to="/analytics" replace />;
};

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/",
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppShell />,
        children: [
          {
            index: true,
            element: <RoleHomeRedirect />,
          },
          {
            path: "admin/home",
            element: <RoleHomeRedirect />,
          },

          // -------------------------------------------------------------
          // Employee Self-Service (ESS) Routes
          // -------------------------------------------------------------
          {
            path: "ess",
            element: <Navigate to="/ess/dashboard" replace />,
          },
          {
            path: "ess/dashboard",
            element: <ESSHomePage />,
          },
          {
            path: "ess/profile",
            element: <MyProfilePage />,
          },
          {
            path: "ess/attendance",
            element: <MyAttendancePage />,
          },
          {
            path: "ess/leave",
            element: <ApplyLeavePage />,
          },
          {
            path: "ess/payslips",
            element: <MyPayslipsPage />,
          },
          {
            path: "ess/documents",
            element: <MyDocumentsPage />,
          },
          {
            path: "ess/requests",
            element: <MyRequestsPage />,
          },
          {
            path: "ess/announcements",
            element: <AnnouncementsPage />,
          },

          // -------------------------------------------------------------
          // Centralized Workflows & Approvals Inbox
          // -------------------------------------------------------------
          {
            path: "approvals",
            element: <ApprovalsInboxPage />,
          },

          // -------------------------------------------------------------
          // CRM & Sales Routes
          // -------------------------------------------------------------
          {
            path: "crm",
            element: <Navigate to="/crm/home" replace />,
          },
          {
            path: "crm/home",
            element: <CRMHomePage />,
          },
          {
            path: "crm/leads",
            element: <LeadsPage />,
          },
          {
            path: "crm/accounts",
            element: <AccountsPage />,
          },
          {
            path: "crm/contacts",
            element: <ContactsPage />,
          },
          {
            path: "crm/opportunities",
            element: <OpportunitiesPage />,
          },
          {
            path: "crm/activities",
            element: <ActivitiesPage />,
          },
          {
            path: "crm/quotations",
            element: <QuotationsPage />,
          },
          {
            path: "crm/orders",
            element: <SalesOrdersPage />,
          },
          {
            path: "crm/reports",
            element: <SalesReportsPage />,
          },

          // -------------------------------------------------------------
          // HR Administration Routes
          // -------------------------------------------------------------
          {
            path: "hr",
            element: <HROverviewPage />,
          },
          {
            path: "hr/employees",
            element: <EmployeesPage />,
          },
          {
            path: "hr/employees/:id",
            element: <EmployeeProfilePage />,
          },
          {
            path: "hr/attendance",
            element: <AttendancePage />,
          },
          {
            path: "hr/leaves",
            element: <LeaveManagementPage />,
          },
          {
            path: "hr/payroll",
            element: <PayrollDashboardPage />,
          },
          {
            path: "hr/recruitment",
            element: <RecruitmentPage />,
          },
          {
            path: "hr/performance",
            element: <PerformancePage />,
          },
          {
            path: "hr/learning",
            element: <LearningPage />,
          },

          // -------------------------------------------------------------
          // AI Platform & Copilot Routes
          // -------------------------------------------------------------
          {
            path: "ai",
            element: <Navigate to="/ai/copilot" replace />,
          },
          {
            path: "ai/copilot",
            element: <AICopilotPage />,
          },
          {
            path: "ai/knowledge",
            element: <AIKnowledgeBasePage />,
          },
          {
            path: "ai/predictive",
            element: <MLPredictivePage />,
          },
          {
            path: "ai/resume",
            element: <ResumeIntelligencePage />,
          },
          {
            path: "ai/forecast",
            element: <SalesForecastingPage />,
          },
          {
            path: "ai/telemetry",
            element: <AIUsageTelemetryPage />,
          },

          // -------------------------------------------------------------
          // Organization Structure Routes
          // -------------------------------------------------------------
          {
            path: "organization",
            element: <OrganizationOverviewPage />,
          },
          {
            path: "organization/branches",
            element: <BranchesPage />,
          },
          {
            path: "organization/departments",
            element: <DepartmentsPage />,
          },
          {
            path: "organization/teams",
            element: <TeamsPage />,
          },
          {
            path: "organization/designations",
            element: <DesignationsPage />,
          },
          {
            path: "organization/business-units",
            element: <BusinessUnitsPage />,
          },
          {
            path: "organization/cost-centers",
            element: <CostCentersPage />,
          },
          {
            path: "organization/locations",
            element: <LocationsPage />,
          },
          {
            path: "organization/calendars",
            element: <CalendarsPage />,
          },
          {
            path: "organization/holidays",
            element: <HolidaysPage />,
          },

          // -------------------------------------------------------------
          // Finance & Accounting Routes
          // -------------------------------------------------------------
          {
            path: "finance",
            element: <FinanceOverviewPage />,
          },
          {
            path: "finance/accounts",
            element: <ChartOfAccountsPage />,
          },
          {
            path: "finance/periods",
            element: <FiscalPeriodsPage />,
          },
          {
            path: "finance/journals",
            element: <JournalEntriesPage />,
          },
          {
            path: "finance/invoices",
            element: <InvoicesPage />,
          },
          {
            path: "finance/bills",
            element: <BillsPage />,
          },
          {
            path: "finance/payments",
            element: <PaymentsPage />,
          },
          {
            path: "finance/banks",
            element: <BankAccountsPage />,
          },
          {
            path: "finance/reports",
            element: <FinancialReportsPage />,
          },

          // -------------------------------------------------------------
          // Analytics & Intelligence Routes
          // -------------------------------------------------------------
          {
            path: "analytics",
            element: <ExecutiveDashboardPage />,
          },
          {
            path: "analytics/finance",
            element: <FinancialAnalyticsPage />,
          },
          {
            path: "analytics/sales",
            element: <SalesAnalyticsPage />,
          },
          {
            path: "analytics/inventory",
            element: <InventoryAnalyticsPage />,
          },
          {
            path: "analytics/manufacturing",
            element: <ManufacturingAnalyticsPage />,
          },
          {
            path: "analytics/hr",
            element: <HRAnalyticsPage />,
          },
          {
            path: "analytics/kpis",
            element: <KPICatalogPage />,
          },
          {
            path: "analytics/reports",
            element: <ReportsHubPage />,
          },

          // -------------------------------------------------------------
          // Supply Chain & Operations (Retained)
          // -------------------------------------------------------------
          {
            path: "inventory",
            element: <InventoryOverviewPage />,
          },
          {
            path: "inventory/products",
            element: <ProductsPage />,
          },
          {
            path: "inventory/warehouses",
            element: <WarehousesPage />,
          },
          {
            path: "inventory/balances",
            element: <StockBalancesPage />,
          },
          {
            path: "inventory/ledger",
            element: <StockLedgerPage />,
          },
          {
            path: "inventory/transfers",
            element: <StockTransfersPage />,
          },
          {
            path: "inventory/adjustments",
            element: <StockAdjustmentsPage />,
          },
          {
            path: "inventory/receipts",
            element: <GoodsReceiptsPage />,
          },
          {
            path: "procurement",
            element: <ProcurementOverviewPage />,
          },
          {
            path: "procurement/suppliers",
            element: <SuppliersPage />,
          },
          {
            path: "procurement/requests",
            element: <PurchaseRequestsPage />,
          },
          {
            path: "procurement/orders",
            element: <PurchaseOrdersPage />,
          },
          {
            path: "manufacturing",
            element: <ManufacturingOverviewPage />,
          },
          {
            path: "manufacturing/boms",
            element: <BillsOfMaterialsPage />,
          },
          {
            path: "manufacturing/routings",
            element: <RoutingsPage />,
          },
          {
            path: "manufacturing/work-centers",
            element: <WorkCentersPage />,
          },
          {
            path: "manufacturing/orders",
            element: <ProductionOrdersPage />,
          },
          {
            path: "manufacturing/work-orders",
            element: <WorkOrdersPage />,
          },
          {
            path: "manufacturing/consumption",
            element: <MaterialConsumptionPage />,
          },
          {
            path: "manufacturing/mrp",
            element: <MRPEnginePage />,
          },
          {
            path: "manufacturing/inspections",
            element: <QualityInspectionsPage />,
          },
          {
            path: "jobs",
            element: <BackgroundJobsDashboardPage />,
          },
          {
            path: "jobs/dashboard",
            element: <BackgroundJobsDashboardPage />,
          },
        ],
      },
    ],
  },
  {
    path: "*",
    element: <Navigate to="/crm/home" replace />,
  },
]);
