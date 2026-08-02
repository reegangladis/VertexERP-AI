import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Menu,
  Search,
  Bell,
  Sparkles,
  Command,
  Building2,
} from 'lucide-react';
import { useUI } from '@/hooks/useUI';
import { ThemeToggle } from './ThemeToggle';
import { useQuery } from '@tanstack/react-query';
import { fetchHealth } from '@/services/api';
import { Button } from './Button';
import { CommandPalette } from './common/CommandPalette';

export function Navbar() {
  const { toggleSidebar } = useUI();
  const [isCommandOpen, setIsCommandOpen] = useState(false);
  const [isNotificationOpen, setIsNotificationOpen] = useState(false);

  // Query API Health for Realtime Indicator
  const { data: health, status: queryStatus } = useQuery({
    queryKey: ['api-health'],
    queryFn: fetchHealth,
    refetchInterval: 15000,
    retry: 1,
  });

  const notifications = [
    { title: 'SOC 2 Audit Report Generated', time: '10m ago', type: 'security' },
    { title: 'Canary Deployment v1.0.0 Traffic Split 100%', time: '25m ago', type: 'deploy' },
    { title: 'XGBoost ML Demand Model Re-trained', time: '1h ago', type: 'ml' },
  ];

  return (
    <>
      <header className="sticky top-0 z-40 w-full border-b border-slate-200/80 dark:border-slate-800/80 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl">
        <div className="flex h-16 items-center justify-between px-4 sm:px-6">
          {/* Left Section: Menu Toggle + Logo */}
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleSidebar}
              className="p-2 h-auto w-auto rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800"
              aria-label="Toggle Navigation Sidebar"
            >
              <Menu className="h-5 w-5 text-slate-600 dark:text-slate-300" />
            </Button>

            <Link to="/" className="flex items-center space-x-2 group">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/20 group-hover:scale-105 transition">
                <Sparkles className="h-4 w-4" />
              </div>
              <span className="font-extrabold text-base tracking-tight font-sans">
                VertexERP <span className="gradient-text font-black">AI</span>
              </span>
            </Link>
          </div>

          {/* Center Section: Global Search Bar */}
          <div className="hidden md:flex items-center max-w-md w-full">
            <button
              onClick={() => setIsCommandOpen(true)}
              className="w-full flex items-center justify-between px-3.5 py-2 rounded-xl bg-slate-100 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700/60 text-xs text-slate-400 hover:border-indigo-500/50 transition shadow-inner"
            >
              <div className="flex items-center gap-2">
                <Search className="h-4 w-4 text-indigo-500" />
                <span>Search modules, actions, or ask AI...</span>
              </div>
              <kbd className="px-2 py-0.5 rounded bg-white dark:bg-slate-900 text-[10px] font-mono font-bold text-slate-500 border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-0.5">
                <Command className="h-3 w-3" /> K
              </kbd>
            </button>
          </div>

          {/* Right Section: Workspace, Notifications, Health, Theme */}
          <div className="flex items-center gap-3">
            {/* Workspace Selector Badge */}
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-xl bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200">
              <Building2 className="h-3.5 w-3.5 text-indigo-500" />
              <span>Vertex Global</span>
            </div>

            {/* Notification Bell Dropdown */}
            <div className="relative">
              <button
                onClick={() => setIsNotificationOpen(!isNotificationOpen)}
                className="p-2 rounded-xl text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 relative transition"
              >
                <Bell className="h-4 w-4" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-indigo-600 rounded-full ring-2 ring-white dark:ring-slate-900" />
              </button>

              {isNotificationOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl p-3 z-50 glass-panel">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800 text-xs font-bold">
                    <span>Notifications</span>
                    <span className="text-[10px] text-indigo-500 font-mono">3 New</span>
                  </div>
                  <div className="space-y-2 mt-2">
                    {notifications.map((n, i) => (
                      <div key={i} className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 text-xs space-y-0.5">
                        <p className="font-semibold text-slate-800 dark:text-slate-200">{n.title}</p>
                        <span className="text-[10px] text-slate-400">{n.time}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Health Status Indicator */}
            <div className="flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700/60 font-mono">
              <span className={`h-2 w-2 rounded-full ${queryStatus === 'pending' ? 'bg-amber-500' : 'bg-emerald-500'} animate-pulse`} />
              <span className="text-[10px] font-bold text-slate-600 dark:text-slate-300 uppercase">
                {queryStatus === 'error' || health?.status === 'unhealthy' ? 'Offline' : 'Online'}
              </span>
            </div>

            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Global Command Palette */}
      <CommandPalette isOpen={isCommandOpen} onClose={() => setIsCommandOpen(false)} />
    </>
  );
}
export default Navbar;
