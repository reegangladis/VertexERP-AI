import { Link } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';

export function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6">
      <div className="p-4 border border-border bg-secondary/20 rounded-full">
        <AlertCircle className="h-8 w-8 text-muted-foreground" />
      </div>
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">Resource Not Found</h2>
        <p className="text-muted-foreground max-w-sm text-sm mx-auto leading-relaxed">
          The console module or workspace page you are trying to access does not exist or has not
          been established in Sprint 1.1.
        </p>
      </div>
      <Link
        to="/"
        className="px-4 py-2 border border-border rounded bg-primary text-primary-foreground text-sm font-medium transition-all select-none cursor-pointer"
      >
        Return to Overview
      </Link>
    </div>
  );
}
export default NotFound;
