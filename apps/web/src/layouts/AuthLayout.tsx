import React from 'react';
import { Outlet } from 'react-router-dom';

export function AuthLayout() {
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
          <p>Phase 1 Security Foundation. Auth portals enabled in Phase 2.</p>
        </div>
      </div>
    </div>
  );
}
export default AuthLayout;
