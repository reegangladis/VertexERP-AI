import React from 'react';
import { Hammer } from 'lucide-react';

export function Maintenance() {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center p-6 select-none">
      <div className="flex items-center justify-center h-20 w-20 rounded-full bg-amber-500/10 mb-6 text-amber-500">
        <Hammer className="h-10 w-10 animate-spin duration-1000" style={{ animationDuration: '3s' }} />
      </div>
      <h1 className="text-3xl font-extrabold tracking-tight text-foreground mb-2">
        System Maintenance
      </h1>
      <h2 className="text-sm font-semibold text-muted-foreground mb-4">
        VertexERP AI is undergoing optimization upgrades
      </h2>
      <p className="text-sm text-muted-foreground max-w-sm leading-relaxed">
        We are completing active maintenance checks. Normal enterprise telemetry access will resume shortly. Thank you for your patience.
      </p>
    </div>
  );
}
export default Maintenance;
