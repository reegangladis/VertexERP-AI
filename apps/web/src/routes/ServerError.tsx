import React from 'react';
import { RefreshCw, ServerCrash } from 'lucide-react';
import { Button } from '@/components/Button';

export function ServerError() {
  const handleReload = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center p-6 select-none">
      <div className="flex items-center justify-center h-20 w-20 rounded-full bg-destructive/10 mb-6 text-destructive">
        <ServerCrash className="h-10 w-10 animate-bounce" />
      </div>
      <h1 className="text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl mb-2">
        500
      </h1>
      <h2 className="text-lg font-semibold text-muted-foreground mb-4">
        Internal Server Error
      </h2>
      <p className="text-sm text-muted-foreground max-w-sm mb-8 leading-relaxed">
        The application gateway encountered an unexpected exception. Our systems are working to resolve the issue.
      </p>
      <Button
        variant="outline"
        onClick={handleReload}
        leftIcon={<RefreshCw className="h-4 w-4" />}
      >
        Retry Request
      </Button>
    </div>
  );
}
export default ServerError;
