import { createBrowserRouter, Navigate } from "react-router-dom";
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

import { HROverviewPage } from "@/features/hr/pages/HROverviewPage";
import { EmployeesPage } from "@/features/hr/pages/EmployeesPage";
import { EmployeeProfilePage } from "@/features/hr/pages/EmployeeProfilePage";
import { AttendancePage } from "@/features/hr/pages/AttendancePage";
import { LeaveManagementPage } from "@/features/hr/pages/LeaveManagementPage";
import { PayrollDashboardPage } from "@/features/hr/pages/PayrollDashboardPage";
import { RecruitmentPage } from "@/features/hr/pages/RecruitmentPage";
import { PerformancePage } from "@/features/hr/pages/PerformancePage";
import { LearningPage } from "@/features/hr/pages/LearningPage";

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

// Background Processing & Jobs Pages
import { BackgroundJobsDashboardPage } from "@/features/jobs";

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
            element: <Navigate to="/inventory" replace />,
          },
          // Inventory Routes
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

          // Procurement Routes
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

          // Manufacturing & MRP Routes
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
            path: "manufacturing/production-orders",
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
            path: "manufacturing/consumptions",
            element: <MaterialConsumptionPage />,
          },
          {
            path: "manufacturing/mrp",
            element: <MRPEnginePage />,
          },
          {
            path: "manufacturing/quality",
            element: <QualityInspectionsPage />,
          },
          {
            path: "manufacturing/quality-inspections",
            element: <QualityInspectionsPage />,
          },

          // HR Domain Routes
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

          // Organization Domain Routes
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

          // Finance Domain Routes
          {
            path: "finance",
            element: <FinanceOverviewPage />,
          },
          {
            path: "finance/accounts",
            element: <ChartOfAccountsPage />,
          },
          {
            path: "finance/fiscal",
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

          // Analytics & Intelligence Routes
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

          // AI Platform & Copilot Routes
          {
            path: "ai",
            element: <AICopilotPage />,
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
            path: "ai/telemetry",
            element: <AIUsageTelemetryPage />,
          },

          // Background Processing & Jobs Routes
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
    element: <Navigate to="/inventory" replace />,
  },
]);
