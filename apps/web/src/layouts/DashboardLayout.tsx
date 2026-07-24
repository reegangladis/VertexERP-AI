import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Sidebar } from '@/components/Sidebar';
import { Footer } from '@/components/Footer';

export function DashboardLayout() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-y-auto">
          <main className="flex-grow p-6 md:p-8 max-w-7xl w-full mx-auto">
            <Outlet />
          </main>
          <Footer />
        </div>
      </div>
    </div>
  );
}
export default DashboardLayout;
