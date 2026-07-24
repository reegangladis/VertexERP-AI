import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { ThemeProvider } from '@/store/ThemeContext';
import { UIProvider } from '@/store/UIContext';
import { NotificationProvider } from '@/store/NotificationContext';
import { SettingsProvider } from '@/store/SettingsContext';

import { AppLayout } from '@/layouts/AppLayout';
import { DashboardLayout } from '@/layouts/DashboardLayout';
import { ErrorBoundary } from '@/components/ErrorBoundary';

import { LandingPage } from '@/pages/LandingPage';
import { DashboardPlaceholder } from '@/pages/DashboardPlaceholder';
import { NotFound } from '@/routes/NotFound';
import { ServerError } from '@/routes/ServerError';
import { Unauthorized } from '@/routes/Unauthorized';
import { Maintenance } from '@/routes/Maintenance';

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
                        <Route path="*" element={<NotFound />} />
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
