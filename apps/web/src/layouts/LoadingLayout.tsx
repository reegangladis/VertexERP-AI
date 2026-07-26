import React from 'react';
import { Spinner } from '@/components/Spinner';

export function LoadingLayout() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground select-none">
      <div className="flex flex-col items-center gap-4">
        <Spinner size="lg" className="text-primary" />
        <p className="text-xs font-medium text-muted-foreground animate-pulse">
          Loading VertexERP AI...
        </p>
      </div>
    </div>
  );
}
export default LoadingLayout;
