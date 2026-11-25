import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search,
  Building2,
  GitFork,
  Users,
  Award,
  Layers,
  DollarSign,
  MapPin,
  Calendar,
  Sun,
  Palmtree,
  Inbox,
  Bot,
  BarChart3,
  Briefcase,
  ArrowRight,
  X,
} from "lucide-react";

interface CommandEntry {
  label: string;
  category: string;
  to: string;
  keywords: string;
  icon: React.ReactNode;
}

const COMMANDS: CommandEntry[] = [
  { label: "Executive Command Center", category: "Analytics", to: "/analytics", keywords: "dashboard executive kpis", icon: <BarChart3 className="w-4 h-4 text-brand-400" /> },
  { label: "Approvals Inbox (Manager Sign-Off)", category: "Governance", to: "/approvals", keywords: "approve reject leave inbox manager", icon: <Inbox className="w-4 h-4 text-rose-400" /> },
  { label: "Apply for Leave & Quotas", category: "ESS", to: "/ess/leave", keywords: "leave vacation pto sick casual apply", icon: <Palmtree className="w-4 h-4 text-emerald-400" /> },
  { label: "Leave Governance & Approval Queue", category: "HRMS", to: "/hr/leaves", keywords: "hr leave manager approve balance", icon: <Palmtree className="w-4 h-4 text-amber-400" /> },
  { label: "Branches Management", category: "Organization", to: "/organization/branches", keywords: "branches offices hq locations", icon: <Building2 className="w-4 h-4 text-brand-400" /> },
  { label: "Departments & Hierarchy Tree", category: "Organization", to: "/organization/departments", keywords: "departments hierarchy tree org", icon: <GitFork className="w-4 h-4 text-amber-400" /> },
  { label: "Teams & Agile Pods", category: "Organization", to: "/organization/teams", keywords: "teams squads members", icon: <Users className="w-4 h-4 text-emerald-400" /> },
  { label: "Designations & Career Levels", category: "Organization", to: "/organization/designations", keywords: "designations titles roles", icon: <Award className="w-4 h-4 text-yellow-400" /> },
  { label: "Business Units (SBUs)", category: "Organization", to: "/organization/business-units", keywords: "business units divisions sbu", icon: <Layers className="w-4 h-4 text-fuchsia-400" /> },
  { label: "Cost Centers & Budgets", category: "Organization", to: "/organization/cost-centers", keywords: "cost centers budgets spend", icon: <DollarSign className="w-4 h-4 text-emerald-400" /> },
  { label: "Facility Locations", category: "Organization", to: "/organization/locations", keywords: "locations warehouses plants offices", icon: <MapPin className="w-4 h-4 text-rose-400" /> },
  { label: "Work Calendars & Shifts", category: "Organization", to: "/organization/calendars", keywords: "work calendars schedules shifts", icon: <Calendar className="w-4 h-4 text-amber-400" /> },
  { label: "Holiday Calendar", category: "Organization", to: "/organization/holidays", keywords: "holidays calendar national", icon: <Sun className="w-4 h-4 text-yellow-400" /> },
  { label: "CRM Sales Pipeline & Leads", category: "CRM", to: "/crm/home", keywords: "crm deals leads pipeline sales", icon: <Briefcase className="w-4 h-4 text-fuchsia-400" /> },
  { label: "Vertex AI Copilot", category: "AI", to: "/ai/copilot", keywords: "ai copilot assistant chat", icon: <Bot className="w-4 h-4 text-brand-400" /> },
];

export const CommandPalette: React.FC<{ isOpen: boolean; onClose: () => void }> = ({
  isOpen,
  onClose,
}) => {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      window.addEventListener("keydown", onKeyDown);
    }
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [isOpen, onClose]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return COMMANDS;
    return COMMANDS.filter(
      (c) =>
        c.label.toLowerCase().includes(q) ||
        c.category.toLowerCase().includes(q) ||
        c.keywords.toLowerCase().includes(q)
    );
  }, [query]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 p-4">
      <div className="fixed inset-0 bg-black/75 backdrop-blur-sm" onClick={onClose} />
      <div className="relative z-10 w-full max-w-xl rounded-2xl border border-zinc-800 bg-zinc-950/95 shadow-2xl shadow-black/90 overflow-hidden">
        <div className="flex items-center gap-3 px-4 py-3.5 border-b border-zinc-800">
          <Search className="w-4 h-4 text-brand-400 shrink-0" />
          <input
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Jump to any module, leave request, branch, or calendar..."
            className="flex-1 bg-transparent text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none"
          />
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="max-h-96 overflow-y-auto p-2 space-y-1">
          {filtered.length === 0 ? (
            <div className="py-10 text-center text-xs text-zinc-500">
              No matching command found for &ldquo;{query}&rdquo;.
            </div>
          ) : (
            filtered.map((cmd) => (
              <button
                key={cmd.to}
                type="button"
                onClick={() => {
                  navigate(cmd.to);
                  setQuery("");
                  onClose();
                }}
                className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-left hover:bg-zinc-900 border border-transparent hover:border-zinc-800 transition-all group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center group-hover:border-brand-500/40">
                    {cmd.icon}
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-zinc-100 group-hover:text-brand-300">
                      {cmd.label}
                    </div>
                    <div className="text-[10px] text-zinc-500">{cmd.category}</div>
                  </div>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-zinc-600 group-hover:text-brand-400 transition-colors" />
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
