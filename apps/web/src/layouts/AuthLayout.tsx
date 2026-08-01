import React, { useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '@/store/AuthContext';

/**
 * AuthLayout — Public layout wrapping auth pages (login, register, etc.)
 *
 * Redirects already-authenticated users away from auth pages to the dashboard.
 * Provides the centered card shell for all auth page content.
 */
export function AuthLayout() {
  const { isAuthenticated, isLoading, getDefaultDashboardRoute } = useAuth();
  const navigate = useNavigate();

  // If the user is already authenticated, redirect to their role-based dashboard
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      navigate(getDefaultDashboardRoute(), { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate, getDefaultDashboardRoute]);

  // While checking auth state, render nothing to avoid a flash of auth UI
  if (isLoading) {
    return null;
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-secondary/20 px-4 py-12 sm:px-6 lg:px-8 select-none">
      <div className="w-full max-w-md space-y-8 bg-card border border-border p-8 rounded-lg shadow-md">
        <div className="text-center">
          <h2 className="text-2xl font-bold tracking-tight text-foreground uppercase">
            VertexERP <span className="text-primary font-light text-lg">AI</span>
          </h2>
          <p className="mt-2 text-xs text-muted-foreground">
            Enterprise AI Operating System
          </p>
        </div>
        
        <Outlet />
        
        <div className="mt-6 text-center text-[10px] text-muted-foreground/60 border-t border-border pt-4">
          <p>Enterprise Authentication &amp; Identity Management · Secured by VertexERP AI</p>
        </div>
      </div>
    </div>
  );
}

export default AuthLayout;
