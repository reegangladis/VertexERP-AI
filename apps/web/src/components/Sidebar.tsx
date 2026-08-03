import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Building2,
  Settings,
  ShieldCheck,
  Calendar,
  MapPin,
  GitBranch,
  Key,
  Shield,
  Wand2,
  User,
  Monitor,
  LogOut,
  FolderTree,
  Building,
  Users,
  Award,
  DollarSign,
  Network,
  UserCheck,
  Clock,
} from 'lucide-react';
import { useUI } from '@/hooks/useUI';
import { useAuth } from '@/store/AuthContext';

export function Sidebar() {
  const { isSidebarOpen } = useUI();
  const { user, logout } = useAuth();

  if (!isSidebarOpen) return null;

  const coreFoundationItems = [
    { label: 'Dashboard', path: '/org/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
    { label: 'Setup Wizard', path: '/org/setup-wizard', icon: <Wand2 className="h-4 w-4" /> },
    { label: 'Organization Profile', path: '/org/profile', icon: <Building2 className="h-4 w-4" /> },
    { label: 'Tenant Settings', path: '/org/tenant-settings', icon: <Settings className="h-4 w-4" /> },
    { label: 'Security Settings', path: '/org/security-settings', icon: <ShieldCheck className="h-4 w-4" /> },
    { label: 'Business Calendar', path: '/org/calendar', icon: <Calendar className="h-4 w-4" /> },
    { label: 'Locations', path: '/org/locations', icon: <MapPin className="h-4 w-4" /> },
    { label: 'Branches', path: '/org/branches', icon: <GitBranch className="h-4 w-4" /> },
  ];

  const hrItems = [
    { label: 'Employee Directory', path: '/hr/employees', icon: <UserCheck className="h-4 w-4" /> },
    { label: 'Attendance & Time', path: '/hr/attendance', icon: <Clock className="h-4 w-4" /> },
    { label: 'Leave & Absence', path: '/hr/leave', icon: <Calendar className="h-4 w-4" /> },
    { label: 'Payroll & Compensation', path: '/hr/payroll', icon: <DollarSign className="h-4 w-4" /> },
    { label: 'Recruitment & Talent', path: '/hr/recruitment', icon: <Briefcase className="h-4 w-4" /> },
    { label: 'Training & L&D', path: '/hr/training', icon: <GraduationCap className="h-4 w-4" /> },
  ];

  const orgStructureItems = [
    { label: 'Departments', path: '/org/departments', icon: <FolderTree className="h-4 w-4" /> },
    { label: 'Business Units', path: '/org/business-units', icon: <Building className="h-4 w-4" /> },
    { label: 'Teams', path: '/org/teams', icon: <Users className="h-4 w-4" /> },
    { label: 'Designations', path: '/org/designations', icon: <Award className="h-4 w-4" /> },
    { label: 'Cost Centers', path: '/org/cost-centers', icon: <DollarSign className="h-4 w-4" /> },
    { label: 'Office Locations', path: '/org/office-locations', icon: <MapPin className="h-4 w-4" /> },
    { label: 'Org Chart', path: '/org/org-chart', icon: <Network className="h-4 w-4" /> },
  ];

  const identityItems = [
    { label: 'Roles', path: '/org/roles', icon: <Shield className="h-4 w-4" /> },
    { label: 'Permissions', path: '/org/permissions', icon: <Key className="h-4 w-4" /> },
    { label: 'My Profile', path: '/profile', icon: <User className="h-4 w-4" /> },
    { label: 'Active Sessions', path: '/sessions', icon: <Monitor className="h-4 w-4" /> },
    { label: 'Account Settings', path: '/settings', icon: <Settings className="h-4 w-4" /> },
  ];

  return (
    <aside className="w-64 border-r border-border bg-card flex flex-col shrink-0 min-h-[calc(100vh-4rem)] select-none">
      <div className="p-4 border-b border-border">
        <h2 className="text-xs uppercase font-mono tracking-wider text-muted-foreground font-semibold">
          VertexERP AI Platform
        </h2>
        <p className="text-[11px] text-muted-foreground mt-0.5">Phase 1-9 HR & L&D</p>
      </div>

      <nav className="flex-1 p-3 space-y-4 overflow-y-auto">
        <div className="space-y-1">
          <p className="px-3 text-[10px] uppercase font-mono tracking-wider text-muted-foreground font-semibold mb-1">
            Core HR
          </p>
          {hrItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 text-xs font-medium rounded-md transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground font-semibold shadow-sm'
                    : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                }`
              }
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>

        <div className="space-y-1 pt-2 border-t border-border/50">
          <p className="px-3 text-[10px] uppercase font-mono tracking-wider text-muted-foreground font-semibold mb-1">
            Foundation
          </p>
          {coreFoundationItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 text-xs font-medium rounded-md transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground font-semibold shadow-sm'
                    : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                }`
              }
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>

        <div className="space-y-1 pt-2 border-t border-border/50">
          <p className="px-3 text-[10px] uppercase font-mono tracking-wider text-muted-foreground font-semibold mb-1">
            Org Structure
          </p>
          {orgStructureItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 text-xs font-medium rounded-md transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground font-semibold shadow-sm'
                    : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                }`
              }
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>

        <div className="space-y-1 pt-2 border-t border-border/50">
          <p className="px-3 text-[10px] uppercase font-mono tracking-wider text-muted-foreground font-semibold mb-1">
            Identity & Security
          </p>
          {identityItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 text-xs font-medium rounded-md transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground font-semibold shadow-sm'
                    : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                }`
              }
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>
      </nav>

      {user && (
        <div className="p-3 border-t border-border bg-secondary/10 flex items-center justify-between">
          <div className="flex items-center gap-2 overflow-hidden">
            <div className="w-7 h-7 rounded-full bg-primary/20 text-primary font-bold text-xs flex items-center justify-center">
              {user.first_name[0]}
            </div>
            <div className="truncate">
              <p className="text-xs font-semibold truncate">{user.first_name} {user.last_name}</p>
              <p className="text-[10px] text-muted-foreground truncate">{user.email}</p>
            </div>
          </div>
          <button
            onClick={() => logout()}
            className="p-1.5 text-muted-foreground hover:text-destructive transition-colors"
            title="Log Out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      )}
    </aside>
  );
}

export default Sidebar;
