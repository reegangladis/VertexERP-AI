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
