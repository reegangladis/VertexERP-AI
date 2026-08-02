import React from 'react';
import { Outlet } from 'react-router-dom';
import { ToastContainer } from '@/components/Toast';

export function AppLayout() {
  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-200">
      <Outlet />
      <ToastContainer />
    </div>
  );
}
export default AppLayout;
