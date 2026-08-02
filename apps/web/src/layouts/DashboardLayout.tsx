import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Sidebar } from '@/components/Sidebar';
import { Footer } from '@/components/Footer';
import { FloatingAIAssistant } from '@/components/common/FloatingAIAssistant';

export function DashboardLayout() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 font-sans">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-y-auto">
          <main className="flex-grow p-4 md:p-6 lg:p-8 max-w-7xl w-full mx-auto space-y-6">
            <Outlet />
          </main>
          <Footer />
        </div>
      </div>
      {/* Centerpiece Floating AI Copilot Assistant */}
      <FloatingAIAssistant />
    </div>
  );
}
export default DashboardLayout;
