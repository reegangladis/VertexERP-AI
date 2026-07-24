import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, Server, Shield, Activity } from 'lucide-react';
import { useUI } from '@/hooks/useUI';
import { ThemeToggle } from './ThemeToggle';
import { useQuery } from '@tanstack/react-query';
import { fetchHealth } from '@/services/api';
import { Button } from './Button';

export function Navbar() {
  const { toggleSidebar } = useUI();
  const location = useLocation();

  // Query API Health for Realtime Indicator
  const { data: health, status: queryStatus } = useQuery({
    queryKey: ['api-health'],
    queryFn: fetchHealth,
    refetchInterval: 15000,
    retry: 1,
  });

  const getHealthColor = () => {
    if (queryStatus === 'pending') return 'bg-yellow-500';
    if (queryStatus === 'error' || health?.status === 'unhealthy') return 'bg-red-500';
    return 'bg-emerald-500';
  };

  const getHealthTitle = () => {
    if (queryStatus === 'pending') return 'API Syncing...';
    if (queryStatus === 'error' || health?.status === 'unhealthy') return 'API Offline';
    return 'API Operational';
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-background/80 backdrop-blur-md">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleSidebar}
            className="p-2 h-auto w-auto rounded hover:bg-muted"
            aria-label="Toggle Navigation Sidebar"
          >
            <Menu className="h-4 w-4" />
          </Button>
          
          <Link to="/" className="flex items-center space-x-2">
            <span className="font-bold text-base tracking-tight uppercase">
              VertexERP <span className="text-primary font-light text-sm">AI</span>
            </span>
          </Link>
        </div>

        <div className="flex items-center gap-4">
          {/* Health Status Indicator */}
          <div
            className="flex items-center gap-1.5 text-xs border border-border px-2 py-0.5 rounded bg-secondary/50 select-none font-mono"
            title={getHealthTitle()}
          >
            <span className={`h-2 w-2 rounded-full ${getHealthColor()} animate-pulse`} />
            <span className="text-muted-foreground uppercase text-[10px]">
              {queryStatus === 'error' || health?.status === 'unhealthy' ? 'Offline' : 'Online'}
            </span>
          </div>

          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
export default Navbar;
