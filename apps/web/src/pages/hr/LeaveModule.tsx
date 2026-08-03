import React, { useState } from 'react';
import {
  Calendar,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Plus,
  FileText,
  UserCheck,
  Award,
  Layers,
  Search,
  Filter,
  Paperclip,
  Check,
  X,
  TrendingUp,
  Globe,
  Briefcase,
  ChevronRight,
} from 'lucide-react';

const mockLeaveBalances = [
  { type: 'Annual Leave (AL)', available: 18.0, pending: 1.0, used: 2.0, total: 20.0, color: 'bg-blue-500' },
  { type: 'Sick Leave (SL)', available: 10.0, pending: 0.0, used: 2.0, total: 12.0, color: 'bg-emerald-500' },
  { type: 'Casual Leave (CL)', available: 6.0, pending: 0.0, used: 1.0, total: 7.0, color: 'bg-amber-500' },
  { type: 'Comp Off (CO)', available: 2.0, pending: 0.0, used: 0.0, total: 2.0, color: 'bg-purple-500' },
];

const mockLeaveRequests = [
  { id: 'lr1', type: 'Annual Leave', startDate: '2026-08-10', endDate: '2026-08-12', days: 3.0, halfDay: false, reason: 'Family summer vacation', status: 'Pending', appliedAt: '2026-08-02' },
  { id: 'lr2', type: 'Sick Leave', startDate: '2026-07-15', endDate: '2026-07-16', days: 2.0, halfDay: false, reason: 'Doctor prescribed rest', status: 'Approved', appliedAt: '2026-07-14' },
];

const mockPendingApprovals = [
  { id: 'pa1', employee: 'John Doe (EMP-102)', department: 'Engineering', type: 'Annual Leave', dates: 'Aug 10 - Aug 12 (3 Days)', reason: 'Family trip', appliedAt: '2026-08-02' },
  { id: 'pa2', employee: 'Alice Smith (EMP-105)', department: 'Product', type: 'Casual Leave', dates: 'Aug 05 (Half Day)', reason: 'Personal errand', appliedAt: '2026-08-03' },
];

const mockHolidays = [
  { date: '2026-09-07', name: 'Labor Day', type: 'National Holiday' },
  { date: '2026-10-12', name: 'Columbus Day / Indigenous Peoples Day', type: 'Federal Holiday' },
  { date: '2026-11-26', name: 'Thanksgiving Day', type: 'National Holiday' },
];

export function LeaveModule() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'history' | 'apply' | 'approvals' | 'types' | 'holidays' | 'compoff'>('dashboard');
  const [isApplyModalOpen, setIsApplyModalOpen] = useState(false);
  const [selectedLeaveType, setSelectedLeaveType] = useState('Annual Leave');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [isHalfDay, setIsHalfDay] = useState(false);
  const [reason, setReason] = useState('');

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-sky-950 to-slate-900 rounded-xl p-6 text-white shadow-xl border border-sky-900/40">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-sky-400 font-mono text-xs uppercase tracking-wider font-semibold mb-1">
              <Calendar className="w-4 h-4" /> Phase 6 — Enterprise Leave & Absence Management
            </div>
            <h1 className="text-2xl font-bold tracking-tight">Leave & Absence Control Hub</h1>
            <p className="text-sm text-slate-300 mt-1">
              Policy-driven leave accruals, holiday calendars, multi-level approvals, comp-off credits & balance engine.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsApplyModalOpen(true)}
              className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold rounded-lg shadow-md transition flex items-center gap-2"
            >
              <Plus className="w-4 h-4" /> Apply for Leave
            </button>
          </div>
        </div>

        {/* Sub-Navigation Tabs */}
        <div className="flex items-center gap-2 mt-6 overflow-x-auto border-t border-slate-800/80 pt-4 scrollbar-none">
          {[
            { id: 'dashboard', label: 'Overview & Balances', icon: <TrendingUp className="w-3.5 h-3.5" /> },
            { id: 'history', label: 'My Leave History', icon: <FileText className="w-3.5 h-3.5" /> },
            { id: 'approvals', label: 'Approvals Queue', icon: <UserCheck className="w-3.5 h-3.5" /> },
            { id: 'types', label: 'Leave Policies & Types', icon: <Layers className="w-3.5 h-3.5" /> },
            { id: 'holidays', label: 'Holiday Calendar', icon: <Globe className="w-3.5 h-3.5" /> },
            { id: 'compoff', label: 'Comp-Off Credits', icon: <Award className="w-3.5 h-3.5" /> },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition flex items-center gap-1.5 whitespace-nowrap ${
                activeTab === tab.id
                  ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* 1. OVERVIEW & BALANCES VIEW */}
      {activeTab === 'dashboard' && (
        <div className="space-y-6">
          {/* Leave Balances Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {mockLeaveBalances.map((b, i) => (
              <div key={i} className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-foreground">{b.type}</span>
                  <div className={`w-3 h-3 rounded-full ${b.color}`} />
                </div>
                <div className="flex items-baseline justify-between">
                  <div>
                    <h3 className="text-2xl font-extrabold text-foreground">{b.available}</h3>
                    <p className="text-[10px] text-muted-foreground font-mono">Available Days</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-semibold text-muted-foreground">{b.used} Used</span>
                    <p className="text-[10px] text-amber-500 font-mono">{b.pending} Pending</p>
                  </div>
                </div>
                <div className="w-full bg-secondary/50 rounded-full h-1.5 overflow-hidden">
                  <div className={`h-full ${b.color}`} style={{ width: `${(b.available / b.total) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>

          {/* Grid Layout: Pending Approvals & Upcoming Holidays */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Approvals Queue Widget */}
            <div className="lg:col-span-2 bg-card p-5 rounded-xl border border-border shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <UserCheck className="w-4 h-4 text-sky-500" /> Pending Approval Requests
                </h3>
                <span className="text-xs text-sky-500 font-mono font-semibold">2 Requests Needing Decision</span>
              </div>
              <div className="space-y-3">
                {mockPendingApprovals.map((pa) => (
                  <div key={pa.id} className="p-4 bg-secondary/20 rounded-xl border border-border/60 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-bold text-foreground">{pa.employee}</p>
                      <p className="text-[11px] text-muted-foreground mt-0.5">{pa.type} — <span className="font-semibold text-foreground">{pa.dates}</span></p>
                      <p className="text-[10px] text-muted-foreground mt-1 italic">"{pa.reason}"</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="p-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold transition">
                        <Check className="w-4 h-4" />
                      </button>
                      <button className="p-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold transition">
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Upcoming Holidays */}
            <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Globe className="w-4 h-4 text-amber-500" /> Upcoming Holidays
                </h3>
                <span className="text-xs text-muted-foreground font-mono">2026 Calendar</span>
              </div>
              <div className="space-y-3">
                {mockHolidays.map((h, idx) => (
                  <div key={idx} className="p-3 bg-secondary/20 rounded-lg border border-border/50 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-semibold text-foreground">{h.name}</p>
                      <p className="text-[10px] text-muted-foreground">{h.type}</p>
                    </div>
                    <span className="px-2.5 py-1 bg-amber-500/10 text-amber-500 font-mono text-[10px] font-bold rounded-md">
                      {h.date}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 2. LEAVE HISTORY VIEW */}
      {activeTab === 'history' && (
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-foreground">My Leave Applications</h3>
            <span className="text-xs text-muted-foreground font-mono">Total 2 Applications</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-secondary/40 text-muted-foreground font-mono uppercase text-[10px]">
                <tr>
                  <th className="p-3">Leave Type</th>
                  <th className="p-3">Start Date</th>
                  <th className="p-3">End Date</th>
                  <th className="p-3">Net Days</th>
                  <th className="p-3">Reason</th>
                  <th className="p-3">Status</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {mockLeaveRequests.map((r) => (
                  <tr key={r.id} className="hover:bg-secondary/10">
                    <td className="p-3 font-semibold text-foreground">{r.type}</td>
                    <td className="p-3 font-mono">{r.startDate}</td>
                    <td className="p-3 font-mono">{r.endDate}</td>
                    <td className="p-3 font-bold text-sky-500">{r.days} days</td>
                    <td className="p-3 max-w-xs truncate">{r.reason}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        r.status === 'Approved' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'
                      }`}>
                        {r.status}
                      </span>
                    </td>
                    <td className="p-3 text-right">
                      {r.status === 'Pending' && (
                        <button className="px-2.5 py-1 bg-rose-600 text-white text-[10px] font-semibold rounded hover:bg-rose-500">
                          Cancel
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* APPLY LEAVE MODAL / DIALOG */}
      {isApplyModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card w-full max-w-lg rounded-2xl border border-border shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-base font-bold text-foreground flex items-center gap-2">
                <Calendar className="w-5 h-5 text-sky-500" /> Apply for Leave
              </h3>
              <button onClick={() => setIsApplyModalOpen(false)} className="text-muted-foreground hover:text-foreground">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold mb-1">Select Leave Type</label>
                <select
                  value={selectedLeaveType}
                  onChange={(e) => setSelectedLeaveType(e.target.value)}
                  className="w-full p-2.5 rounded-lg border border-border bg-background text-foreground"
                >
                  <option>Annual Leave (AL)</option>
                  <option>Sick Leave (SL)</option>
                  <option>Casual Leave (CL)</option>
                  <option>Comp Off (CO)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-semibold mb-1">Start Date</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full p-2.5 rounded-lg border border-border bg-background text-foreground"
                  />
                </div>
                <div>
                  <label className="block font-semibold mb-1">End Date</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full p-2.5 rounded-lg border border-border bg-background text-foreground"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="halfday"
                  checked={isHalfDay}
                  onChange={(e) => setIsHalfDay(e.target.checked)}
                  className="rounded border-border text-sky-600 focus:ring-sky-500"
                />
                <label htmlFor="halfday" className="font-semibold cursor-pointer">
                  Half-Day Leave Session
                </label>
              </div>

              <div>
                <label className="block font-semibold mb-1">Reason for Leave</label>
                <textarea
                  rows={3}
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="Provide details for manager approval..."
                  className="w-full p-2.5 rounded-lg border border-border bg-background text-foreground"
                />
              </div>

              <div className="p-3 bg-sky-500/10 rounded-lg border border-sky-500/20 text-sky-400 font-mono text-[11px] flex justify-between">
                <span>Calculated Net Days:</span>
                <span className="font-bold">1.0 Working Day (Weekends/Holidays Excluded)</span>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-3 border-t border-border">
              <button
                onClick={() => setIsApplyModalOpen(false)}
                className="px-4 py-2 bg-secondary text-foreground text-xs font-semibold rounded-lg hover:bg-secondary/80"
              >
                Cancel
              </button>
              <button
                onClick={() => setIsApplyModalOpen(false)}
                className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold rounded-lg shadow transition"
              >
                Submit Leave Application
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default LeaveModule;
