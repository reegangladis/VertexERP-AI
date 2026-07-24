import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Lock } from 'lucide-react';
import { Button } from '@/components/Button';

export function Unauthorized() {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center p-6 select-none">
      <div className="flex items-center justify-center h-20 w-20 rounded-full bg-destructive/10 mb-6 text-destructive">
        <Lock className="h-10 w-10" />
      </div>
      <h1 className="text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl mb-2">
        403
      </h1>
      <h2 className="text-lg font-semibold text-muted-foreground mb-4">
        Access Denied
      </h2>
      <p className="text-sm text-muted-foreground max-w-sm mb-8 leading-relaxed">
        Your user identity does not contain the permissions required to view this module.
      </p>
      <Link to="/">
        <Button variant="outline" leftIcon={<ArrowLeft className="h-4 w-4" />}>
          Back to Overview
        </Button>
      </Link>
    </div>
  );
}
export default Unauthorized;
