import React from 'react';

export function ErrorLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-destructive/5 px-4 py-12 select-none">
      <div className="w-full max-w-md bg-card border border-destructive/20 p-8 rounded-lg shadow-lg text-center space-y-6 animate-in fade-in zoom-in-95 duration-200">
        {children}
      </div>
    </div>
  );
}
export default ErrorLayout;
