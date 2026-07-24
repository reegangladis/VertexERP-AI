import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Home,
  Users,
  Briefcase,
  Layers,
  Settings,
  Shield,
  HelpCircle,
} from 'lucide-react';
import { useUI } from '@/hooks/useUI';

export function Sidebar() {
  const { isSidebarOpen } = useUI();

  if (!isSidebarOpen) return null;

  const menuItems = [
    { label: 'Overview', path: '/', icon: <Home className="h-4 w-4" /> },
    { label: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
  ];

  const placeholderItems = [
    { label: 'Identity Management', icon: <Shield className="h-4 w-4" /> },
    { label: 'HR Portal', icon: <Briefcase className="h-4 w-4" /> },
    { label: 'CRM & Clients', icon: <Users className="h-4 w-4" /> },
    { label: 'System Settings', icon: <Settings className="h-4 w-4" /> },
  ];

  return (
    <aside className="w-64 border-r border-border bg-card shrink-0 h-[calc(100vh-4rem)] flex flex-col justify-between p-4 select-none">
      <div className="space-y-6">
        <div>
          <h3 className="px-3 text-xs font-semibold text-muted-foreground/60 uppercase tracking-wider mb-3">
            Core Platform
          </h3>
          <nav className="space-y-1">
            {menuItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                  }`
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        <div>
          <h3 className="px-3 text-xs font-semibold text-muted-foreground/60 uppercase tracking-wider mb-3">
            Phase 2 Placeholders
          </h3>
          <nav className="space-y-1 opacity-60">
            {placeholderItems.map((item, index) => (
              <div
                key={index}
                className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-muted-foreground cursor-not-allowed hover:bg-secondary/40"
                title="Available in Phase 2"
              >
                {item.icon}
                <span>{item.label}</span>
                <span className="ml-auto text-[9px] uppercase px-1 border border-border rounded bg-secondary scale-90">
                  Soon
                </span>
              </div>
            ))}
          </nav>
        </div>
      </div>

      <div className="border-t border-border pt-4 text-xs text-muted-foreground/60 text-center">
        <p className="font-mono">Foundation Completion</p>
      </div>
    </aside>
  );
}
export default Sidebar;
