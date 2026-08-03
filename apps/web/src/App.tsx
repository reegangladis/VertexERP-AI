import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { ThemeProvider } from '@/store/ThemeContext';
import { UIProvider } from '@/store/UIContext';
import { NotificationProvider } from '@/store/NotificationContext';
import { SettingsProvider } from '@/store/SettingsContext';
import { AuthProvider, useAuth } from '@/store/AuthContext';

import { DashboardLayout } from '@/layouts/DashboardLayout';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { ProtectedRoute } from '@/components/ProtectedRoute';

import { NotFound } from '@/routes/NotFound';

// Phase 2 Identity & Authentication Pages
import {
  Login,
  Register,
  ForgotPassword,
  ResetPassword,
  VerifyEmail,
  SessionExpired,
  Unauthorized,
} from '@/pages/AuthPages';

// Phase 1 Core Foundation Pages
import { OrgDashboard } from '@/pages/org/Dashboard';
import { SetupWizard } from '@/pages/org/SetupWizard';
import { OrgProfile } from '@/pages/org/Profile';
import { OrgBranches } from '@/pages/org/Branches';
import { OrgLocations } from '@/pages/org/Locations';
import { OrgBusinessCalendar } from '@/pages/org/BusinessCalendar';
import { OrgSettings } from '@/pages/org/Settings';
import { TenantSettings } from '@/pages/TenantSettings';
import { UserSettings } from '@/pages/UserSettings';
import { SessionsPage } from '@/pages/admin/SessionsPage';
import { RoleManagement, PermissionManagement } from '@/pages/IdentityManagement';
import { IdentityDashboard } from '@/pages/IdentityDashboard';
import { MfaSettingsPage } from '@/pages/MfaSettings';

// Phase 3 Enterprise Organization Structure Pages
import {
  DepartmentsPage,
  BusinessUnitsPage,
  TeamsPage,
  DesignationsPage,
  CostCentersPage,
  OfficeLocationsPage,
  OrgChartPage,
} from '@/pages/org/OrgStructurePages';

// Phase 4 Core HR & Phase 5 Attendance & Phase 6 Leave & Phase 7 Payroll & Phase 8 Recruitment & Phase 9 Training
import { EmployeeDirectoryPage, EmployeeProfileDetailPage } from '@/pages/hr/EmployeePages';
import { AttendanceModule } from '@/pages/hr/AttendanceModule';
import { LeaveModule } from '@/pages/hr/LeaveModule';
import { PayrollModule } from '@/pages/hr/PayrollModule';
import { RecruitmentModule } from '@/pages/hr/RecruitmentModule';
import { PerformanceModule } from '@/pages/hr/PerformanceModule';
import { TrainingModule } from '@/pages/hr/TrainingModule';
import { CrmModule } from '@/pages/crm/CrmModule';
import { InventoryModule } from '@/pages/inventory/InventoryModule';
import { FinanceModule } from '@/pages/finance/FinanceModule';
import { ManufacturingModule } from '@/pages/manufacturing/ManufacturingModule';
import { AiModule } from '@/pages/ai/AiModule';
import { AnalyticsModule } from '@/pages/analytics/AnalyticsModule';
import { OpsModule } from '@/pages/ops/OpsModule';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function RootRedirect() {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return null;
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }
  return <Navigate to="/org/dashboard" replace />;
}

export function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <UIProvider>
            <NotificationProvider>
              <SettingsProvider>
                <BrowserRouter>
                  <AuthProvider>
                    <Routes>
                      {/* Root Redirect */}
                      <Route path="/" element={<RootRedirect />} />
                      <Route path="/dashboard" element={<Navigate to="/org/dashboard" replace />} />

                      {/* Public Auth Routes */}
                      <Route path="/login" element={<Navigate to="/auth/login" replace />} />
                      <Route path="/register" element={<Navigate to="/auth/register" replace />} />
                      <Route path="/auth/login" element={<Login />} />
                      <Route path="/auth/register" element={<Register />} />
                      <Route path="/auth/forgot-password" element={<ForgotPassword />} />
                      <Route path="/auth/reset-password" element={<ResetPassword />} />
                      <Route path="/auth/verify-email" element={<VerifyEmail />} />
                      <Route path="/auth/session-expired" element={<SessionExpired />} />
                      <Route path="/unauthorized" element={<Unauthorized />} />

                      {/* Protected Application Routes */}
                      <Route element={<ProtectedRoute />}>
                        <Route element={<DashboardLayout />}>
                          {/* Phase 1 Core */}
                          <Route path="/org/dashboard" element={<OrgDashboard />} />
                          <Route path="/org/setup-wizard" element={<SetupWizard />} />
                          <Route path="/org/profile" element={<OrgProfile />} />
                          <Route path="/profile" element={<OrgProfile />} />
                          <Route path="/org/tenant-settings" element={<TenantSettings />} />
                          <Route path="/org/security-settings" element={<OrgSettings />} />
                          <Route path="/org/calendar" element={<OrgBusinessCalendar />} />
                          <Route path="/org/locations" element={<OrgLocations />} />
                          <Route path="/org/branches" element={<OrgBranches />} />

                          {/* Phase 2 Identity */}
                          <Route path="/identity/dashboard" element={<IdentityDashboard />} />
                          <Route path="/identity/mfa" element={<MfaSettingsPage />} />
                          <Route path="/org/roles" element={<RoleManagement />} />
                          <Route path="/org/permissions" element={<PermissionManagement />} />
                          <Route path="/sessions" element={<SessionsPage />} />
                          <Route path="/settings" element={<UserSettings />} />

                          {/* Phase 3 Organization Structure */}
                          <Route path="/org/departments" element={<DepartmentsPage />} />
                          <Route path="/org/business-units" element={<BusinessUnitsPage />} />
                          <Route path="/org/teams" element={<TeamsPage />} />
                          <Route path="/org/designations" element={<DesignationsPage />} />
                          <Route path="/org/cost-centers" element={<CostCentersPage />} />
                          <Route path="/org/office-locations" element={<OfficeLocationsPage />} />
                          <Route path="/org/org-chart" element={<OrgChartPage />} />

                          {/* Phase 4 Core HR */}
                          <Route path="/hr/employees" element={<EmployeeDirectoryPage />} />
                          <Route path="/hr/employees/:id" element={<EmployeeProfileDetailPage />} />

                          {/* Phase 5 Attendance & Time Management */}
                          <Route path="/hr/attendance" element={<AttendanceModule />} />

                          {/* Phase 6 Leave & Absence Management */}
                          <Route path="/hr/leave" element={<LeaveModule />} />

                          {/* Phase 7 Payroll & Compensation Management */}
                          <Route path="/hr/payroll" element={<PayrollModule />} />

                          {/* Phase 8 Recruitment & Talent Acquisition */}
                          <Route path="/hr/recruitment" element={<RecruitmentModule />} />

                          {/* Phase 9 Performance & Learning Platform */}
                          <Route path="/hr/performance" element={<PerformanceModule />} />
                          <Route path="/hr/training" element={<TrainingModule />} />

                          {/* Phase 10 Enterprise CRM & Sales Platform */}
                          <Route path="/crm" element={<CrmModule />} />
                          <Route path="/crm/dashboard" element={<CrmModule />} />
                          <Route path="/sales" element={<CrmModule />} />

                          {/* Phase 11 Enterprise Inventory & Procurement Platform */}
                          <Route path="/inventory" element={<InventoryModule />} />
                          <Route path="/inventory/dashboard" element={<InventoryModule />} />
                          <Route path="/procurement" element={<InventoryModule />} />
                          <Route path="/warehouses" element={<InventoryModule />} />

                          {/* Phase 12 Enterprise Finance & Accounting Platform */}
                          <Route path="/finance" element={<FinanceModule />} />
                          <Route path="/finance/dashboard" element={<FinanceModule />} />
                          <Route path="/finance/accounts" element={<FinanceModule />} />
                          <Route path="/finance/journals" element={<FinanceModule />} />
                          <Route path="/finance/invoices" element={<FinanceModule />} />
                          <Route path="/finance/bills" element={<FinanceModule />} />
                          <Route path="/finance/payments" element={<FinanceModule />} />
                          <Route path="/finance/banks" element={<FinanceModule />} />

                          {/* Phase 13 Enterprise Manufacturing & MRP Platform */}
                          <Route path="/manufacturing" element={<ManufacturingModule />} />
                          <Route path="/manufacturing/dashboard" element={<ManufacturingModule />} />
                          <Route path="/manufacturing/bom" element={<ManufacturingModule />} />
                          <Route path="/manufacturing/production-orders" element={<ManufacturingModule />} />
                          <Route path="/manufacturing/work-centers" element={<ManufacturingModule />} />
                          <Route path="/manufacturing/machines" element={<ManufacturingModule />} />
                          <Route path="/manufacturing/mrp" element={<ManufacturingModule />} />
                          <Route path="/manufacturing/quality" element={<ManufacturingModule />} />

                          {/* Phase 14 Enterprise AI, RAG & Copilot Platform */}
                          <Route path="/ai" element={<AiModule />} />
                          <Route path="/ai/dashboard" element={<AiModule />} />
                          <Route path="/ai/copilot" element={<AiModule />} />
                          <Route path="/ai/knowledge" element={<AiModule />} />
                          <Route path="/ai/prompts" element={<AiModule />} />
                          <Route path="/ai/agents" element={<AiModule />} />

                          {/* Phase 15 Enterprise Data Engineering, Analytics & MLOps Platform */}
                          <Route path="/analytics" element={<AnalyticsModule />} />
                          <Route path="/analytics/dashboard" element={<AnalyticsModule />} />
                          <Route path="/analytics/datasets" element={<AnalyticsModule />} />
                          <Route path="/analytics/pipelines" element={<AnalyticsModule />} />
                          <Route path="/analytics/features" element={<AnalyticsModule />} />
                          <Route path="/analytics/models" element={<AnalyticsModule />} />
                          <Route path="/analytics/predictions" element={<AnalyticsModule />} />
                          <Route path="/analytics/drift" element={<AnalyticsModule />} />

                          {/* Phase 16 Enterprise Integration, Observability & Production Platform */}
                          <Route path="/ops" element={<OpsModule />} />
                          <Route path="/ops/dashboard" element={<OpsModule />} />
                          <Route path="/ops/api-keys" element={<OpsModule />} />
                          <Route path="/ops/webhooks" element={<OpsModule />} />
                          <Route path="/ops/notifications" element={<OpsModule />} />
                          <Route path="/ops/monitoring" element={<OpsModule />} />
                          <Route path="/ops/deployments" element={<OpsModule />} />
                          <Route path="/ops/backups" element={<OpsModule />} />
                        </Route>
                      </Route>

                      {/* 404 Fallback */}
                      <Route path="*" element={<NotFound />} />
                    </Routes>
                  </AuthProvider>
                </BrowserRouter>
              </SettingsProvider>
            </NotificationProvider>
          </UIProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
