import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { ThemeProvider } from '@/store/ThemeContext';
import { UIProvider } from '@/store/UIContext';
import { NotificationProvider } from '@/store/NotificationContext';
import { SettingsProvider } from '@/store/SettingsContext';

import { AppLayout } from '@/layouts/AppLayout';
import { DashboardLayout } from '@/layouts/DashboardLayout';
import { AuthLayout } from '@/layouts/AuthLayout';
import { ErrorBoundary } from '@/components/ErrorBoundary';

import { LandingPage } from '@/pages/LandingPage';
import { DashboardPlaceholder } from '@/pages/DashboardPlaceholder';
import { NotFound } from '@/routes/NotFound';
import { ServerError } from '@/routes/ServerError';
import { Unauthorized } from '@/routes/Unauthorized';
import { Maintenance } from '@/routes/Maintenance';

// Identity & Settings Page Views
import { Login, Register, ForgotPassword, ResetPassword, VerifyEmail, SessionExpired } from '@/pages/AuthPages';
import { UserManagement, RoleManagement, PermissionManagement } from '@/pages/IdentityManagement';
import { UserSettings } from '@/pages/UserSettings';
import { TenantSettings } from '@/pages/TenantSettings';

// Organization Management Page Views
import { OrgDashboard } from '@/pages/org/Dashboard';
import { OrgProfile } from '@/pages/org/Profile';
import { OrgBranches } from '@/pages/org/Branches';
import { OrgDepartments } from '@/pages/org/Departments';
import { OrgTeams } from '@/pages/org/Teams';
import { OrgDesignations } from '@/pages/org/Designations';
import { OrgLocations } from '@/pages/org/Locations';
import { OrgReportingStructure } from '@/pages/org/ReportingStructure';
import { OrgBusinessCalendar } from '@/pages/org/BusinessCalendar';
import { OrgSettings } from '@/pages/org/Settings';

// HR Intelligence Platform Page Views
import { HRDashboard } from '@/pages/hr/Dashboard';
import { HREmployeeList } from '@/pages/hr/EmployeeList';
import { HREmployeeDetails } from '@/pages/hr/EmployeeDetails';
import { HRAttendance } from '@/pages/hr/Attendance';
import { HRLeaveManagement } from '@/pages/hr/LeaveManagement';
import { HRRecruitment } from '@/pages/hr/Recruitment';
import { HRPerformance } from '@/pages/hr/Performance';
import { HRTraining } from '@/pages/hr/Training';
import { HRDocuments } from '@/pages/hr/Documents';
import { HRPayroll } from '@/pages/hr/Payroll';

// CRM Intelligence Platform Page Views
import { CRMDashboard } from '@/pages/crm/Dashboard';
import { CRMCustomers } from '@/pages/crm/Customers';
import { CRMCustomerDetails } from '@/pages/crm/CustomerDetails';
import { CRMLeads } from '@/pages/crm/Leads';
import { CRMPipeline } from '@/pages/crm/Pipeline';
import { CRMDeals } from '@/pages/crm/Deals';
import { CRMActivities } from '@/pages/crm/Activities';
import { CRMSupportTickets } from '@/pages/crm/SupportTickets';
import { CRMCampaigns } from '@/pages/crm/Campaigns';

// Inventory & Warehouse Platform Page Views
import { InventoryDashboard } from '@/pages/inventory/Dashboard';
import { InventoryProducts } from '@/pages/inventory/Products';
import { InventoryCategories } from '@/pages/inventory/Categories';
import { InventoryWarehouses } from '@/pages/inventory/Warehouses';
import { InventoryWarehouseDetails } from '@/pages/inventory/WarehouseDetails';
import { InventorySuppliers } from '@/pages/inventory/Suppliers';
import { InventoryPurchaseOrders } from '@/pages/inventory/PurchaseOrders';
import { InventoryStockTransfers } from '@/pages/inventory/StockTransfers';
import { InventoryCounts } from '@/pages/inventory/InventoryCounts';

// Finance & Accounting Platform Page Views
import { FinanceDashboard } from '@/pages/finance/FinanceDashboard';
import { ChartOfAccountsPage } from '@/pages/finance/ChartOfAccountsPage';
import { JournalEntriesPage } from '@/pages/finance/JournalEntriesPage';
import { InvoicesPage } from '@/pages/finance/InvoicesPage';
import { BillsPage } from '@/pages/finance/BillsPage';
import { ExpensesPage } from '@/pages/finance/ExpensesPage';
import { BudgetsPage } from '@/pages/finance/BudgetsPage';
import { TaxesPage } from '@/pages/finance/TaxesPage';
import { FixedAssetsPage } from '@/pages/finance/FixedAssetsPage';
import { BankAccountsPage } from '@/pages/finance/BankAccountsPage';
import { FinancialReportsPage } from '@/pages/finance/FinancialReportsPage';

// Manufacturing & Production Intelligence Platform Page Views
import {
  ManufacturingDashboard,
  BillOfMaterialsPage,
  RoutingsPage,
  WorkCentersPage,
  MachinesPage,
  ProductionOrdersPage,
// Business Intelligence & Analytics Platform Page Views
import {
  ExecutiveDashboard,
  HRAnalyticsPage,
  CRMAnalyticsPage,
  InventoryAnalyticsPage,
  FinanceAnalyticsPage,
  ManufacturingAnalyticsPage,
  CustomReportsPage,
  DashboardBuilderPage,
} from '@/pages/analytics';

// Enterprise Data Engineering Platform Page Views
import {
  DataEngineeringDashboard,
  PipelineMonitor,
  DatasetExplorer,
  FeatureStorePage,
  MetadataCatalogPage,
  DataQualityDashboard,
  LineageViewer,
} from '@/pages/data-engineering';

// Enterprise Machine Learning Platform Page Views
import {
  MLDashboard,
  ModelRegistry,
  TrainingJobs,
  ExperimentsPage,
  PredictionsPage,
  EvaluationMetricsPage,
} from '@/pages/ml';


// Setup TanStack Query Client

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <SettingsProvider>
        <NotificationProvider>
          <UIProvider>
            <ThemeProvider>
              <ErrorBoundary>
                <BrowserRouter>
                  <Routes>
                    {/* AppLayout manages Global Toast notifications */}
                    <Route element={<AppLayout />}>
                      
                      {/* DashboardLayout coordinates Navbar and Sidebar navigations */}
                      <Route element={<DashboardLayout />}>
                        <Route path="/" element={<LandingPage />} />
                        <Route path="dashboard" element={<DashboardPlaceholder />} />
                        <Route path="unauthorized" element={<Unauthorized />} />
                        <Route path="maintenance" element={<Maintenance />} />
                        <Route path="500" element={<ServerError />} />
                        
                        {/* Organization Management */}
                        <Route path="org/dashboard" element={<OrgDashboard />} />
                        <Route path="org/profile" element={<OrgProfile />} />
                        <Route path="org/branches" element={<OrgBranches />} />
                        <Route path="org/departments" element={<OrgDepartments />} />
                        <Route path="org/teams" element={<OrgTeams />} />
                        <Route path="org/designations" element={<OrgDesignations />} />
                        <Route path="org/locations" element={<OrgLocations />} />
                        <Route path="org/reporting" element={<OrgReportingStructure />} />
                        <Route path="org/calendar" element={<OrgBusinessCalendar />} />
                        <Route path="org/settings" element={<OrgSettings />} />

                        {/* HR Intelligence Platform */}
                        <Route path="hr/dashboard" element={<HRDashboard />} />
                        <Route path="hr/employees" element={<HREmployeeList />} />
                        <Route path="hr/employees/:id" element={<HREmployeeDetails />} />
                        <Route path="hr/attendance" element={<HRAttendance />} />
                        <Route path="hr/leaves" element={<HRLeaveManagement />} />
                        <Route path="hr/recruitment" element={<HRRecruitment />} />
                        <Route path="hr/performance" element={<HRPerformance />} />
                        <Route path="hr/training" element={<HRTraining />} />
                        <Route path="hr/documents" element={<HRDocuments />} />
                        <Route path="hr/payroll" element={<HRPayroll />} />

                        {/* CRM Intelligence Platform */}
                        <Route path="crm/dashboard" element={<CRMDashboard />} />
                        <Route path="crm/customers" element={<CRMCustomers />} />
                        <Route path="crm/customers/:id" element={<CRMCustomerDetails />} />
                        <Route path="crm/leads" element={<CRMLeads />} />
                        <Route path="crm/pipeline" element={<CRMPipeline />} />
                        <Route path="crm/deals" element={<CRMDeals />} />
                        <Route path="crm/activities" element={<CRMActivities />} />
                        <Route path="crm/support-tickets" element={<CRMSupportTickets />} />
                        <Route path="crm/campaigns" element={<CRMCampaigns />} />

                        {/* Inventory & Warehouse Platform */}
                        <Route path="inventory/dashboard" element={<InventoryDashboard />} />
                        <Route path="inventory/products" element={<InventoryProducts />} />
                        <Route path="inventory/categories" element={<InventoryCategories />} />
                        <Route path="inventory/warehouses" element={<InventoryWarehouses />} />
                        <Route path="inventory/warehouses/:id" element={<InventoryWarehouseDetails />} />
                        <Route path="inventory/suppliers" element={<InventorySuppliers />} />
                        <Route path="inventory/purchase-orders" element={<InventoryPurchaseOrders />} />
                        <Route path="inventory/transfers" element={<InventoryStockTransfers />} />
                        <Route path="inventory/counts" element={<InventoryCounts />} />

                        {/* Finance & Accounting Intelligence Platform */}
                        <Route path="finance/dashboard" element={<FinanceDashboard />} />
                        <Route path="finance/accounts" element={<ChartOfAccountsPage />} />
                        <Route path="finance/journals" element={<JournalEntriesPage />} />
                        <Route path="finance/invoices" element={<InvoicesPage />} />
                        <Route path="finance/bills" element={<BillsPage />} />
                        <Route path="finance/expenses" element={<ExpensesPage />} />
                        <Route path="finance/budgets" element={<BudgetsPage />} />
                        <Route path="finance/taxes" element={<TaxesPage />} />
                        <Route path="finance/assets" element={<FixedAssetsPage />} />
                        <Route path="finance/banking" element={<BankAccountsPage />} />
                        <Route path="finance/reports" element={<FinancialReportsPage />} />

                        {/* Manufacturing & Production Intelligence Platform */}
                        <Route path="manufacturing/dashboard" element={<ManufacturingDashboard />} />
                        <Route path="manufacturing/boms" element={<BillOfMaterialsPage />} />
                        <Route path="manufacturing/routings" element={<RoutingsPage />} />
                        <Route path="manufacturing/work-centers" element={<WorkCentersPage />} />
                        <Route path="manufacturing/machines" element={<MachinesPage />} />
                        <Route path="manufacturing/production-orders" element={<ProductionOrdersPage />} />
                        <Route path="manufacturing/shop-floor" element={<ShopFloorPage />} />
                        <Route path="manufacturing/quality" element={<QualityControlPage />} />
                        <Route path="manufacturing/maintenance" element={<MaintenancePage />} />
                        <Route path="manufacturing/mrp" element={<MRPPage />} />

                        {/* Business Intelligence & Analytics Platform */}
                        <Route path="analytics/executive" element={<ExecutiveDashboard />} />
                        <Route path="analytics/hr" element={<HRAnalyticsPage />} />
                        <Route path="analytics/crm" element={<CRMAnalyticsPage />} />
                        <Route path="analytics/inventory" element={<InventoryAnalyticsPage />} />
                        <Route path="analytics/finance" element={<FinanceAnalyticsPage />} />
                        <Route path="analytics/manufacturing" element={<ManufacturingAnalyticsPage />} />
                        <Route path="analytics/reports" element={<CustomReportsPage />} />
                        <Route path="analytics/builder" element={<DashboardBuilderPage />} />

                        {/* Enterprise Data Engineering Platform */}
                        <Route path="data-engineering/dashboard" element={<DataEngineeringDashboard />} />
                        <Route path="data-engineering/pipelines" element={<PipelineMonitor />} />
                        <Route path="data-engineering/datasets" element={<DatasetExplorer />} />
                        <Route path="data-engineering/feature-store" element={<FeatureStorePage />} />
                        <Route path="data-engineering/metadata" element={<MetadataCatalogPage />} />
                        <Route path="data-engineering/quality" element={<DataQualityDashboard />} />
                        <Route path="data-engineering/lineage" element={<LineageViewer />} />

                        {/* Enterprise Machine Learning Platform */}
                        <Route path="ml/dashboard" element={<MLDashboard />} />
                        <Route path="ml/registry" element={<ModelRegistry />} />
                        <Route path="ml/training" element={<TrainingJobs />} />
                        <Route path="ml/experiments" element={<ExperimentsPage />} />
                        <Route path="ml/predictions" element={<PredictionsPage />} />
                        <Route path="ml/evaluation" element={<EvaluationMetricsPage />} />



                        {/* Security & Identity Dashboards */}
                        <Route path="admin/users" element={<UserManagement />} />
                        <Route path="admin/roles" element={<RoleManagement />} />
                        <Route path="admin/permissions" element={<PermissionManagement />} />
                        <Route path="admin/settings" element={<TenantSettings />} />
                        
                        {/* Account Settings */}
                        <Route path="settings/profile" element={<UserSettings />} />
                        
                        <Route path="*" element={<NotFound />} />
                      </Route>

                      {/* AuthLayout wraps public recovery and credential pages */}
                      <Route path="auth" element={<AuthLayout />}>
                        <Route path="login" element={<Login />} />
                        <Route path="register" element={<Register />} />
                        <Route path="forgot-password" element={<ForgotPassword />} />
                        <Route path="reset-password" element={<ResetPassword />} />
                        <Route path="verify-email" element={<VerifyEmail />} />
                        <Route path="session-expired" element={<SessionExpired />} />
                      </Route>
                      
                    </Route>
                  </Routes>
                </BrowserRouter>
              </ErrorBoundary>
            </ThemeProvider>
          </UIProvider>
        </NotificationProvider>
      </SettingsProvider>
    </QueryClientProvider>
  );
}

export default App;
