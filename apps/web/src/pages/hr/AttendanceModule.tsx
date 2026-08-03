import React, { useState } from 'react';
import {
  Clock,
  Calendar,
  UserCheck,
  UserX,
  AlertCircle,
  TrendingUp,
  MapPin,
  Cpu,
  Layers,
  CheckCircle2,
  XCircle,
  Plus,
  Search,
  Filter,
  RefreshCw,
  Sliders,
  Shield,
  FileText,
  Smartphone,
  Radio,
  Building,
} from 'lucide-react';

// Mock data & initial states for rich interactive demonstration
const mockStats = {
  totalEmployees: 248,
  presentToday: 215,
  absentToday: 12,
  lateToday: 15,
  overtimeToday: 42.5,
  remoteToday: 38,
  onDutyToday: 6,
  attendanceRate: 95.2,
};

const mockShifts = [
  { id: 's1', name: 'General Morning Shift', code: 'SHIFT-GEN', start: '09:00', end: '17:00', grace: 15, break: 60, status: 'Active' },
  { id: 's2', name: 'Evening Support Shift', code: 'SHIFT-EVE', start: '16:00', end: '00:00', grace: 15, break: 60, status: 'Active' },
  { id: 's3', name: 'Night Operations Shift', code: 'SHIFT-NIGHT', start: '00:00', end: '08:00', grace: 10, break: 45, status: 'Active' },
];

const mockCorrections = [
  { id: 'c1', employee: 'Sarah Jenkins (EMP-104)', date: '2026-08-02', reqIn: '09:00 AM', reqOut: '05:30 PM', reason: 'Biometric terminal offline', status: 'Pending' },
  { id: 'c2', employee: 'David Chen (EMP-112)', date: '2026-08-01', reqIn: '08:45 AM', reqOut: '05:00 PM', reason: 'On-site client meeting punch failure', status: 'Approved' },
];

const mockOvertime = [
  { id: 'o1', employee: 'Michael Scott (EMP-101)', date: '2026-08-02', hours: 3.5, reason: 'Month-end financial audit closing', status: 'Pending' },
  { id: 'o2', employee: 'Emily Watson (EMP-118)', date: '2026-08-01', hours: 2.0, reason: 'Emergency server patching', status: 'Approved' },
];

const mockDevices = [
  { id: 'd1', name: 'HQ Gate 1 Biometric Scanner', code: 'BIO-HQ-01', type: 'Fingerprint & Face', ip: '192.168.1.102', location: 'Lobby Entrance', status: 'Online' },
  { id: 'd2', name: 'Branch 2 RFID Turnstile', code: 'RFID-B2-04', type: 'RFID Card', ip: '192.168.2.55', location: 'Turnstile A', status: 'Online' },
];

export function AttendanceModule() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'daily' | 'checkin' | 'shifts' | 'corrections' | 'overtime' | 'devices' | 'geofence'>('dashboard');
  const [isCheckedIn, setIsCheckedIn] = useState(false);
  const [punchTime, setPunchTime] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const handleCheckIn = () => {
    setIsCheckedIn(true);
    setPunchTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
  };

  const handleCheckOut = () => {
    setIsCheckedIn(false);
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-xl p-6 text-white shadow-xl border border-indigo-900/40">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs uppercase tracking-wider font-semibold mb-1">
              <Clock className="w-4 h-4" /> Phase 5 — Enterprise Attendance & Time Management
            </div>
            <h1 className="text-2xl font-bold tracking-tight">Attendance & Time Tracking Hub</h1>
            <p className="text-sm text-slate-300 mt-1">
              Real-time shift scheduling, biometric integration, geofencing, overtime approvals & attendance analytics.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setActiveTab('checkin')}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg shadow-md transition flex items-center gap-2"
            >
              <Clock className="w-4 h-4" /> Punch Clock Widget
            </button>
          </div>
        </div>

        {/* Module Sub-Navigation Tabs */}
        <div className="flex items-center gap-2 mt-6 overflow-x-auto border-t border-slate-800/80 pt-4 scrollbar-none">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: <TrendingUp className="w-3.5 h-3.5" /> },
            { id: 'daily', label: 'Daily Attendance', icon: <UserCheck className="w-3.5 h-3.5" /> },
            { id: 'checkin', label: 'Check-In / Out', icon: <Clock className="w-3.5 h-3.5" /> },
            { id: 'shifts', label: 'Shifts & Rosters', icon: <Layers className="w-3.5 h-3.5" /> },
            { id: 'corrections', label: 'Corrections', icon: <FileText className="w-3.5 h-3.5" /> },
            { id: 'overtime', label: 'Overtime', icon: <Sliders className="w-3.5 h-3.5" /> },
            { id: 'devices', label: 'Biometric Devices', icon: <Cpu className="w-3.5 h-3.5" /> },
            { id: 'geofence', label: 'Geofencing', icon: <MapPin className="w-3.5 h-3.5" /> },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition flex items-center gap-1.5 whitespace-nowrap ${
                activeTab === tab.id
                  ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* 1. DASHBOARD VIEW */}
      {activeTab === 'dashboard' && (
        <div className="space-y-6">
          {/* Summary KPIs */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
            <div className="bg-card p-4 rounded-xl border border-border shadow-sm">
              <p className="text-[11px] font-medium text-muted-foreground uppercase">Present Today</p>
              <h3 className="text-xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">{mockStats.presentToday}</h3>
              <span className="text-[10px] text-muted-foreground font-mono">{mockStats.attendanceRate}% Rate</span>
            </div>

            <div className="bg-card p-4 rounded-xl border border-border shadow-sm">
              <p className="text-[11px] font-medium text-muted-foreground uppercase">Absent</p>
              <h3 className="text-xl font-bold text-rose-600 dark:text-rose-400 mt-1">{mockStats.absentToday}</h3>
              <span className="text-[10px] text-muted-foreground font-mono">Unexcused</span>
            </div>

            <div className="bg-card p-4 rounded-xl border border-border shadow-sm">
              <p className="text-[11px] font-medium text-muted-foreground uppercase">Late Arrivals</p>
              <h3 className="text-xl font-bold text-amber-600 dark:text-amber-400 mt-1">{mockStats.lateToday}</h3>
              <span className="text-[10px] text-muted-foreground font-mono">Grace exceed</span>
            </div>

            <div className="bg-card p-4 rounded-xl border border-border shadow-sm">
              <p className="text-[11px] font-medium text-muted-foreground uppercase">Overtime Hours</p>
              <h3 className="text-xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">{mockStats.overtimeToday} hrs</h3>
              <span className="text-[10px] text-muted-foreground font-mono">Today's Total</span>
            </div>

            <div className="bg-card p-4 rounded-xl border border-border shadow-sm">
              <p className="text-[11px] font-medium text-muted-foreground uppercase">Remote Employees</p>
              <h3 className="text-xl font-bold text-cyan-600 dark:text-cyan-400 mt-1">{mockStats.remoteToday}</h3>
              <span className="text-[10px] text-muted-foreground font-mono">Web/Mobile</span>
            </div>

            <div className="bg-card p-4 rounded-xl border border-border shadow-sm">
              <p className="text-[11px] font-medium text-muted-foreground uppercase">On Duty</p>
              <h3 className="text-xl font-bold text-purple-600 dark:text-purple-400 mt-1">{mockStats.onDutyToday}</h3>
              <span className="text-[10px] text-muted-foreground font-mono">Field Visit</span>
            </div>

            <div className="bg-card p-4 rounded-xl border border-border shadow-sm">
              <p className="text-[11px] font-medium text-muted-foreground uppercase">Total Workforce</p>
              <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100 mt-1">{mockStats.totalEmployees}</h3>
              <span className="text-[10px] text-muted-foreground font-mono">Enrolled</span>
            </div>
          </div>

          {/* Grid Layout: Shift Status & Live Punch Feed */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-card p-5 rounded-xl border border-border shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Layers className="w-4 h-4 text-indigo-500" /> Shift Operational Breakdown
                </h3>
                <span className="text-xs text-muted-foreground font-mono">Today's Roster</span>
              </div>
              <div className="space-y-3">
                {mockShifts.map((shift) => (
                  <div key={shift.id} className="p-3 bg-secondary/20 rounded-lg border border-border/50 flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-xs text-foreground">{shift.name}</span>
                        <span className="px-2 py-0.5 bg-indigo-500/10 text-indigo-500 text-[10px] font-mono rounded font-semibold">
                          {shift.code}
                        </span>
                      </div>
                      <p className="text-[11px] text-muted-foreground mt-0.5">
                        Timing: {shift.start} - {shift.end} | Grace: {shift.grace} mins | Break: {shift.break} mins
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400">98% On Time</span>
                      <p className="text-[10px] text-muted-foreground">82 Active Employees</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions & Terminal Health */}
            <div className="bg-card p-5 rounded-xl border border-border shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Radio className="w-4 h-4 text-emerald-500 animate-pulse" /> Terminal Devices
                </h3>
                <span className="text-xs text-emerald-500 font-semibold font-mono">2 / 2 Online</span>
              </div>
              <div className="space-y-3">
                {mockDevices.map((dev) => (
                  <div key={dev.id} className="p-3 bg-secondary/20 rounded-lg border border-border/50 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-semibold text-foreground">{dev.name}</p>
                      <p className="text-[10px] text-muted-foreground font-mono">{dev.type} ({dev.ip})</p>
                    </div>
                    <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-500 text-[10px] font-semibold rounded">
                      {dev.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 2. CHECK-IN / CHECK-OUT PUNCH WIDGET */}
      {activeTab === 'checkin' && (
        <div className="max-w-xl mx-auto bg-card p-8 rounded-2xl border border-border shadow-lg text-center space-y-6">
          <div className="w-16 h-16 rounded-full bg-indigo-500/10 text-indigo-500 mx-auto flex items-center justify-center">
            <Clock className="w-8 h-8" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-foreground">Interactive Punch Clock</h2>
            <p className="text-xs text-muted-foreground mt-1">
              Check in or check out with automatic GPS geofence validation and shift calculations.
            </p>
          </div>

          <div className="p-4 bg-secondary/30 rounded-xl border border-border text-left space-y-2">
            <div className="flex justify-between text-xs font-medium">
              <span className="text-muted-foreground">Assigned Shift:</span>
              <span className="font-semibold text-foreground">General Day Shift (09:00 - 17:00)</span>
            </div>
            <div className="flex justify-between text-xs font-medium">
              <span className="text-muted-foreground">Geofence Status:</span>
              <span className="text-emerald-500 font-semibold flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5" /> Inside HQ Perimeter (40.7128, -74.0060)
              </span>
            </div>
            {punchTime && (
              <div className="flex justify-between text-xs font-medium">
                <span className="text-muted-foreground">Check-in Time:</span>
                <span className="font-bold text-indigo-500">{punchTime}</span>
              </div>
            )}
          </div>

          <div className="flex justify-center gap-4">
            {!isCheckedIn ? (
              <button
                onClick={handleCheckIn}
                className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm rounded-xl shadow-lg transition flex items-center justify-center gap-2"
              >
                <UserCheck className="w-4 h-4" /> Clock In Now
              </button>
            ) : (
              <button
                onClick={handleCheckOut}
                className="w-full py-3 bg-rose-600 hover:bg-rose-500 text-white font-semibold text-sm rounded-xl shadow-lg transition flex items-center justify-center gap-2"
              >
                <UserX className="w-4 h-4" /> Clock Out Now
              </button>
            )}
          </div>
        </div>
      )}

      {/* 3. SHIFTS MANAGEMENT VIEW */}
      {activeTab === 'shifts' && (
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-foreground">Work Shift Catalog</h3>
              <p className="text-xs text-muted-foreground">Manage organization work shifts, timings, grace period, and break durations.</p>
            </div>
            <button className="px-3 py-1.5 bg-primary text-primary-foreground text-xs font-semibold rounded-md shadow-sm transition flex items-center gap-1.5">
              <Plus className="w-4 h-4" /> Add Work Shift
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-secondary/40 text-muted-foreground font-mono uppercase text-[10px]">
                <tr>
                  <th className="p-3">Shift Name</th>
                  <th className="p-3">Code</th>
                  <th className="p-3">Timing</th>
                  <th className="p-3">Break Duration</th>
                  <th className="p-3">Grace Time</th>
                  <th className="p-3">Weekly Hours</th>
                  <th className="p-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {mockShifts.map((s) => (
                  <tr key={s.id} className="hover:bg-secondary/10">
                    <td className="p-3 font-semibold text-foreground">{s.name}</td>
                    <td className="p-3 font-mono text-indigo-500">{s.code}</td>
                    <td className="p-3">{s.start} - {s.end}</td>
                    <td className="p-3">{s.break} mins</td>
                    <td className="p-3">{s.grace} mins</td>
                    <td className="p-3 font-mono">{shift_weekly(s)}</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-500 font-semibold rounded text-[10px]">
                        {s.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 4. CORRECTIONS VIEW */}
      {activeTab === 'corrections' && (
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-foreground">Attendance Corrections</h3>
              <p className="text-xs text-muted-foreground">Review and approve attendance manual correction requests.</p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-secondary/40 text-muted-foreground font-mono uppercase text-[10px]">
                <tr>
                  <th className="p-3">Employee</th>
                  <th className="p-3">Date</th>
                  <th className="p-3">Req In</th>
                  <th className="p-3">Req Out</th>
                  <th className="p-3">Reason</th>
                  <th className="p-3">Status</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {mockCorrections.map((c) => (
                  <tr key={c.id} className="hover:bg-secondary/10">
                    <td className="p-3 font-semibold text-foreground">{c.employee}</td>
                    <td className="p-3 font-mono">{c.date}</td>
                    <td className="p-3 font-mono">{c.reqIn}</td>
                    <td className="p-3 font-mono">{c.reqOut}</td>
                    <td className="p-3 max-w-xs truncate">{c.reason}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        c.status === 'Approved' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'
                      }`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="p-3 text-right space-x-2">
                      {c.status === 'Pending' && (
                        <>
                          <button className="px-2 py-1 bg-emerald-600 text-white rounded text-[10px] font-semibold hover:bg-emerald-500">
                            Approve
                          </button>
                          <button className="px-2 py-1 bg-rose-600 text-white rounded text-[10px] font-semibold hover:bg-rose-500">
                            Reject
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 5. OVERTIME REQUESTS VIEW */}
      {activeTab === 'overtime' && (
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-foreground">Overtime Request Workflow</h3>
              <p className="text-xs text-muted-foreground">Manage overtime hours approvals and payroll inputs.</p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-secondary/40 text-muted-foreground font-mono uppercase text-[10px]">
                <tr>
                  <th className="p-3">Employee</th>
                  <th className="p-3">Date</th>
                  <th className="p-3">Requested Hours</th>
                  <th className="p-3">Reason</th>
                  <th className="p-3">Status</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {mockOvertime.map((o) => (
                  <tr key={o.id} className="hover:bg-secondary/10">
                    <td className="p-3 font-semibold text-foreground">{o.employee}</td>
                    <td className="p-3 font-mono">{o.date}</td>
                    <td className="p-3 font-mono text-indigo-500 font-bold">{o.hours} hrs</td>
                    <td className="p-3 max-w-xs truncate">{o.reason}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        o.status === 'Approved' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'
                      }`}>
                        {o.status}
                      </span>
                    </td>
                    <td className="p-3 text-right space-x-2">
                      {o.status === 'Pending' && (
                        <button className="px-2.5 py-1 bg-indigo-600 text-white rounded text-[10px] font-semibold hover:bg-indigo-500">
                          Approve OT
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
    </div>
  );
}

function shift_weekly(s: any): string {
  return `${s.weekly || 40} hrs/wk`;
}

export default AttendanceModule;
