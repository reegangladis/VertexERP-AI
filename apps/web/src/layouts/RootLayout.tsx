import { Outlet, Link, useLocation } from 'react-router-dom';
import { ThemeToggle } from '@/components/ThemeToggle';
import { useQuery } from '@tanstack/react-query';
import { fetchHealth } from '@/services/api';

export function RootLayout() {
  const location = useLocation();

  // Polling backend health to display operational status in the UI
  const { data: health, status: queryStatus } = useQuery({
    queryKey: ['api-health'],
    queryFn: fetchHealth,
    refetchInterval: 15000, // Polling frequency 15s
    retry: 1,
    refetchOnWindowFocus: true,
  });

  const getHealthIndicator = () => {
    if (queryStatus === 'pending') {
      return (
        <span className="flex h-2 w-2 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
          <span
            className="relative inline-flex rounded-full h-2 w-2 bg-yellow-500"
            title="Querying backend health..."
          ></span>
        </span>
      );
    }
    if (queryStatus === 'error' || health?.status === 'unhealthy') {
      return (
        <span className="flex h-2 w-2">
          <span
            className="inline-flex rounded-full h-2 w-2 bg-red-500"
            title="API Status: Unreachable or Offline"
          ></span>
        </span>
      );
    }
    return (
      <span className="flex h-2 w-2 relative">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
        <span
          className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"
          title="API Status: Operational"
        ></span>
      </span>
    );
  };

  const getHealthLabel = () => {
    if (queryStatus === 'pending') return 'Syncing...';
    if (queryStatus === 'error' || health?.status === 'unhealthy') return 'Offline';
    return 'Online';
  };

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground transition-colors duration-200">
      {/* Navbar Container */}
      <header className="sticky top-0 z-40 w-full border-b border-border bg-background/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex h-16 items-center justify-between">
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight uppercase">
                VertexERP <span className="text-muted-foreground font-light text-base">AI</span>
              </span>
            </Link>
            <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
              <Link
                to="/"
                className={`transition-colors duration-150 hover:text-foreground/90 ${
                  location.pathname === '/'
                    ? 'text-foreground border-b-2 border-foreground py-5'
                    : 'text-muted-foreground'
                }`}
              >
                Overview
              </Link>
              <Link
                to="/dashboard"
                className={`transition-colors duration-150 hover:text-foreground/90 ${
                  location.pathname === '/dashboard'
                    ? 'text-foreground border-b-2 border-foreground py-5'
                    : 'text-muted-foreground'
                }`}
              >
                Dashboard
              </Link>
            </nav>
          </div>

          <div className="flex items-center space-x-4">
            {/* Realtime API status indicator */}
            <div className="flex items-center space-x-2 text-xs border border-border px-2.5 py-1 rounded bg-secondary/50 select-none">
              {getHealthIndicator()}
              <span className="font-mono text-muted-foreground uppercase">{getHealthLabel()}</span>
            </div>

            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Page Content Outlet */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Footer Container */}
      <footer className="border-t border-border bg-secondary/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col md:flex-row items-center justify-between text-xs text-muted-foreground gap-4">
          <p>© {new Date().getFullYear()} VertexERP AI. Enterprise AI Operating System.</p>
          <div className="flex space-x-6">
            <Link to="/" className="hover:underline transition-all">
              Overview
            </Link>
            <Link to="/dashboard" className="hover:underline transition-all">
              Dashboard
            </Link>
            <a href="/docs/Architecture.md" className="hover:underline transition-all">
              Docs
            </a>
            <span className="text-border">|</span>
            <span className="font-mono">Sprint 1.1 Foundation</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
export default RootLayout;
