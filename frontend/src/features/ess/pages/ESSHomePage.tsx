import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuthStore } from "@/stores/auth-store";
import { useDemoStore } from "@/lib/demo-store";
import { essApi } from "../api/essApi";
import { formatCurrency } from "@/lib/utils";
import { StatCard } from "@/components/ui/StatCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Button } from "@/components/ui/Button";
import {
  Clock,
  LogIn,
  LogOut,
  Calendar,
  CalendarCheck,
  CalendarX,
  FileText,
  Palmtree,
} from "lucide-react";

export const ESSHomePage: React.FC = () => {
  const { fullName, email, userId } = useAuthStore();
  const demoState = useDemoStore();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [isCheckedIn, setIsCheckedIn] = useState(false);
  const [checkInTime, setCheckInTime] = useState<string | null>(null);
  const [checkOutTime, setCheckOutTime] = useState<string | null>(null);
  const [totalHoursToday, setTotalHoursToday] = useState("0h 0m");
  const [actionLoading, setActionLoading] = useState(false);

  // Live digital clock
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const handlePunchIn = async () => {
    setActionLoading(true);
    try {
      const nowStr = new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
      await essApi.clockIn(userId || "emp-current");
      setIsCheckedIn(true);
      setCheckInTime(nowStr);
    } catch {
      const nowStr = new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
      setIsCheckedIn(true);
      setCheckInTime(nowStr);
    } finally {
      setActionLoading(false);
    }
  };

  const handlePunchOut = async () => {
    setActionLoading(true);
    try {
      const nowStr = new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
      await essApi.clockOut(userId || "emp-current");
      setIsCheckedIn(false);
      setCheckOutTime(nowStr);
      setTotalHoursToday("8h 15m");
    } catch {
      const nowStr = new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
      setIsCheckedIn(false);
      setCheckOutTime(nowStr);
      setTotalHoursToday("8h 15m");
    } finally {
      setActionLoading(false);
    }
  };

  const upcomingHolidays = demoState.holidays.slice(0, 4);
  const totalLeaveTaken = demoState.leaveBalances.reduce((acc, b) => acc + b.used, 0);

  return (
    <div className="space-y-6">
      {/* Welcome Banner & Virtual Punch Widget */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Welcome card */}
        <div className="lg:col-span-2 p-6 rounded-2xl border border-zinc-800 bg-gradient-to-br from-zinc-900 via-zinc-900 to-brand-950/30 backdrop-blur-md flex flex-col justify-between shadow-xl">
          <div>
            <span className="text-xs font-bold uppercase tracking-widest text-brand-400">
              Employee Self-Service Workspace
            </span>
            <h1 className="mt-2 text-2xl font-bold text-zinc-50">
              Good day, {fullName || "Colleague"}!
            </h1>
            <p className="mt-1 text-xs text-zinc-400">
              You are signed in as <span className="text-zinc-200 font-medium">{email}</span>. Here is your live
              attendance terminal, leave balances, and approval tracker.
            </p>
          </div>

          <div className="mt-6 pt-4 border-t border-zinc-800/80 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-zinc-800 border border-zinc-700 flex items-center justify-center text-zinc-200">
                <Clock className="w-5 h-5 text-brand-400" />
              </div>
              <div>
                <div className="text-xs text-zinc-400">Current Time</div>
                <div className="text-sm font-bold text-zinc-100">
                  {currentTime.toLocaleTimeString("en-US", {
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                  })}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-xs text-zinc-400">Today&apos;s Status</div>
                <div className="text-xs font-bold">
                  {isCheckedIn ? (
                    <span className="text-emerald-400 flex items-center gap-1 justify-end">
                      <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                      CLOCKED IN
                    </span>
                  ) : checkOutTime ? (
                    <span className="text-zinc-300">CLOCKED OUT</span>
                  ) : (
                    <span className="text-amber-400">NOT CLOCKED IN</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Real-time Punch Terminal Card */}
        <div className="p-6 rounded-2xl border border-zinc-800 bg-zinc-900/80 backdrop-blur-md flex flex-col justify-between shadow-xl">
          <div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                Shift Terminal
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-zinc-800 text-brand-300 border border-zinc-700">
                General 09:00 - 18:00
              </span>
            </div>

            <div className="mt-4 p-3 rounded-xl bg-zinc-950/70 border border-zinc-800 space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-zinc-400">Punch In Time:</span>
                <span className="font-semibold text-zinc-200">{checkInTime || "--:--"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-400">Punch Out Time:</span>
                <span className="font-semibold text-zinc-200">{checkOutTime || "--:--"}</span>
              </div>
              <div className="flex justify-between border-t border-zinc-800 pt-2">
                <span className="text-zinc-400">Duration:</span>
                <span className="font-bold text-brand-400">{totalHoursToday}</span>
              </div>
            </div>
          </div>

          <div className="mt-4">
            {!isCheckedIn ? (
              <Button
                variant="primary"
                onClick={handlePunchIn}
                isLoading={actionLoading}
                className="w-full flex items-center justify-center gap-2 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-lg shadow-emerald-950/40"
              >
                <LogIn className="w-4 h-4" />
                <span>Web Punch In</span>
              </Button>
            ) : (
              <Button
                variant="danger"
                onClick={handlePunchOut}
                isLoading={actionLoading}
                className="w-full flex items-center justify-center gap-2 py-2.5 bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs shadow-lg shadow-rose-950/40"
              >
                <LogOut className="w-4 h-4" />
                <span>Web Punch Out</span>
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Monthly Attendance Overview KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard
          title="Present Days"
          value="19"
          change="On track"
          changeType="increase"
          icon={<CalendarCheck className="w-4 h-4 text-emerald-400" />}
          description="In November 2026"
        />
        <StatCard
          title="Absent Days"
          value="0"
          change="Zero loss"
          changeType="increase"
          icon={<CalendarX className="w-4 h-4 text-rose-400" />}
          description="No unexcused absences"
        />
        <StatCard
          title="Leave Taken"
          value={`${totalLeaveTaken.toFixed(1)} days`}
          change="Synced"
          changeType="neutral"
          icon={<Palmtree className="w-4 h-4 text-amber-400" />}
          description="Approved utilization"
        />
        <StatCard
          title="Avg Hours / Day"
          value="8.4 hrs"
          change="+0.4h"
          changeType="increase"
          icon={<Clock className="w-4 h-4 text-brand-400" />}
          description="Compliant with policy"
        />
      </div>

      {/* Live Leave Balances Quick Grid */}
      <div className="p-6 rounded-2xl border border-zinc-800 bg-zinc-900/60 backdrop-blur-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-zinc-100">My Live Leave Balances</h3>
            <p className="text-xs text-zinc-400">Available quota automatically reflects manager approvals</p>
          </div>
          <Link
            to="/ess/leave"
            className="text-xs text-brand-400 hover:text-brand-300 font-semibold"
          >
            Apply Leave &rarr;
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {demoState.leaveBalances.map((b) => (
            <div key={b.code} className="p-4 rounded-xl border border-zinc-800 bg-zinc-950/70 space-y-1.5">
              <span className="text-xs font-semibold text-zinc-400">{b.name} ({b.code})</span>
              <div className="text-2xl font-bold text-zinc-100">{b.balance.toFixed(1)}</div>
              <div className="text-[11px] text-zinc-400">
                Remaining out of {b.total.toFixed(1)}
                {b.pending > 0 && <span className="text-amber-400 ml-1">({b.pending}d pending)</span>}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Section: Upcoming Holidays & Recent Payslip Snapshot */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Holidays */}
        <div className="p-6 rounded-2xl border border-zinc-800 bg-zinc-900/60 backdrop-blur-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-zinc-100 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-brand-400" />
              <span>Upcoming Official Holidays</span>
            </h3>
            <Link to="/organization/holidays" className="text-[11px] text-brand-400 hover:underline">
              Full Calendar &rarr;
            </Link>
          </div>
          <div className="divide-y divide-zinc-800/80 text-xs">
            {upcomingHolidays.map((h) => (
              <div key={h.id} className="py-2.5 flex items-center justify-between">
                <div>
                  <div className="font-semibold text-zinc-200">{h.name}</div>
                  <div className="text-[11px] text-zinc-400">{h.holiday_type}</div>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-zinc-800 text-zinc-300 border border-zinc-700">
                  {h.holiday_date}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Latest Payslip Quick View */}
        <div className="p-6 rounded-2xl border border-zinc-800 bg-zinc-900/60 backdrop-blur-sm space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-zinc-100 flex items-center gap-2">
                <FileText className="w-4 h-4 text-emerald-400" />
                <span>Latest Payslip (October 2026)</span>
              </h3>
              <StatusBadge status="PAID" />
            </div>

            <div className="mt-4 p-4 rounded-xl bg-zinc-950/70 border border-zinc-800 space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-zinc-400">Gross Earnings:</span>
                <span className="font-semibold text-zinc-200">{formatCurrency(7500.0)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-400">Total Deductions (PF/Tax):</span>
                <span className="font-semibold text-rose-400">-{formatCurrency(1250.0)}</span>
              </div>
              <div className="flex justify-between border-t border-zinc-800 pt-2 text-sm">
                <span className="font-semibold text-zinc-200">Net Take-Home Pay:</span>
                <span className="font-bold text-emerald-400">{formatCurrency(6250.0)}</span>
              </div>
            </div>
          </div>

          <div className="pt-2">
            <Link
              to="/ess/payslips"
              className="inline-flex items-center justify-center w-full px-4 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-xs font-semibold text-zinc-200 transition-colors"
            >
              View Full Payslip & Breakdown &rarr;
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
