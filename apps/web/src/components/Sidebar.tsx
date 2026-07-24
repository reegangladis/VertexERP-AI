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
  ShieldAlert,
  User,
  History,
  Lock,
} from 'lucide-react';
import { useUI } from '@/hooks/useUI';

export function Sidebar() {
  const { isSidebarOpen } = useUI();

  if (!isSidebarOpen) return null;

  const coreItems = [
    { label: 'Overview', path: '/', icon: <Home className="h-4 w-4" /> },
    { label: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
  ];

  const adminItems = [
    { label: 'User Administration', path: '/admin/users', icon: <Users className="h-4 w-4" /> },
    { label: 'Role Mapping', path: '/admin/roles', icon: <Shield className="h-4 w-4" /> },
    { label: 'Permission Matrix', path: '/admin/permissions', icon: <Lock className="h-4 w-4" /> },
    { label: 'Tenant Administration', path: '/admin/settings', icon: <Settings className="h-4 w-4" /> },
  ];

  const userItems = [
    { label: 'Account Settings', path: '/settings/profile', icon: <User className="h-4 w-4" /> },
  ];

  const placeholderItems = [
    { label: 'HR Portal', icon: <Briefcase className="h-4 w-4" /> },
    { label: 'CRM & Clients', icon: <Users className="h-4 w-4" /> },
  ];

  return (
    <aside className="w-64 border-r border-border bg-card shrink-0 h-[calc(100vh-4rem)] flex flex-col justify-between p-4 select-none">
      <div className="space-y-6 overflow-y-auto pr-1">
        
        {/* Core Platform */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            Core Platform
          </h3>
          <nav className="space-y-0.5">
            {coreItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
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

        {/* Security & Identity */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            Security & Identity
          </h3>
          <nav className="space-y-0.5">
            {adminItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
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

        {/* User Account */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            User Account
          </h3>
          <nav className="space-y-0.5">
            {userItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
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

        {/* Phase 3 Placeholders */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            ERP Business Modules
          </h3>
          <nav className="space-y-0.5 opacity-60">
            {placeholderItems.map((item, index) => (
              <div
                key={index}
                className="flex items-center gap-3 px-3 py-1.5 text-xs font-medium rounded-md text-muted-foreground cursor-not-allowed hover:bg-secondary/40"
                title="Available in Phase 3"
              >
                {item.icon}
                <span>{item.label}</span>
                <span className="ml-auto text-[8px] uppercase px-1 border border-border rounded bg-secondary scale-90">
                  Soon
                </span>
              </div>
            ))}
          </nav>
        </div>
      </div>

      <div className="border-t border-border pt-3 text-[10px] text-muted-foreground/60 text-center">
        <p className="font-mono">Phase 2 Platform Complete</p>
      </div>
    </aside>
  );
}
export default Sidebar;
