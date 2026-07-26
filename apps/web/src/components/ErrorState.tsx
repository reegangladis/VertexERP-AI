import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Button } from './Button';

interface ErrorStateProps {
  title?: string;
  description?: string;
  error?: Error | string;
  onRetry?: () => void;
}

export function ErrorState({
  title = 'An error occurred',
  description = 'There was a problem loading this section.',
  error,
  onRetry,
}: ErrorStateProps) {
  const errorMessage = error instanceof Error ? error.message : error;

  return (
    <div className="flex flex-col items-center justify-center p-8 border border-destructive/20 rounded-lg bg-destructive/5 text-center min-h-[300px]">
      <div className="flex items-center justify-center h-16 w-16 rounded-full bg-destructive/10 mb-4 text-destructive">
        <AlertTriangle className="h-10 w-10" />
      </div>
      <h3 className="text-base font-semibold text-foreground mb-1">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-sm mb-4">{description}</p>
      {errorMessage && (
        <code className="text-xs font-mono bg-background border border-border px-3 py-1.5 rounded text-destructive max-w-md break-all mb-6">
          {errorMessage}
        </code>
      )}
      {onRetry && (
        <Button variant="outline" onClick={onRetry}>
          Try Again
        </Button>
      )}
    </div>
  );
}
export default ErrorState;
