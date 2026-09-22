import React, { useEffect, useState } from "react";
import { CalendarOff, Plus, Check, X, Clock, Calendar } from "lucide-react";
import { hrApi } from "../api/hrApi";
import { LeaveBalance, LeaveRequest, LeaveType } from "../types";

export const LeaveManagementPage: React.FC = () => {
  const [types, setTypes] = useState<LeaveType[]>([]);
  const [requests, setRequests] = useState<LeaveRequest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadLeaves() {
      try {
        const [tRes, rRes] = await Promise.allSettled([
          hrApi.getLeaveTypes(),
          hrApi.getLeaveRequests(),
        ]);
        if (tRes.status === "fulfilled") setTypes(tRes.value);
        if (rRes.status === "fulfilled") setRequests(rRes.value);
      } finally {
        setLoading(false);
      }
    }
    loadLeaves();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <CalendarOff className="w-6 h-6 text-amber-400" />
            Leave Management & Entitlements
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">
            Annual leave quotas, policy rules, and manager approval queues.
          </p>
        </div>
      </div>

      {/* Leave Quota Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-xs text-slate-400">Annual Paid Leave</div>
          <div className="text-2xl font-bold text-white mt-1">20.0 Days</div>
          <div className="text-xs text-slate-500 mt-1">Accrual: Monthly • Max Carry: 5 Days</div>
        </div>
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-xs text-slate-400">Sick & Medical Leave</div>
          <div className="text-2xl font-bold text-white mt-1">10.0 Days</div>
          <div className="text-xs text-slate-500 mt-1">Accrual: Annual Quota • Paid</div>
        </div>
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-xs text-slate-400">Parental / Maternity Leave</div>
          <div className="text-2xl font-bold text-white mt-1">90.0 Days</div>
          <div className="text-xs text-slate-500 mt-1">Statutory Standard • 100% Paid</div>
        </div>
      </div>

      {/* Approval Queue Table */}
      <div className="rounded-xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
        <div className="px-6 py-4 border-b border-slate-800 font-semibold text-sm text-slate-200">
          Pending & Recent Leave Requests
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/60 text-slate-400 uppercase text-[11px] font-semibold tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-3.5">Dates</th>
                <th className="px-6 py-3.5">Days</th>
                <th className="px-6 py-3.5">Reason</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              <tr className="hover:bg-slate-800/40">
                <td className="px-6 py-4 text-xs font-medium text-slate-200">2024-06-10 to 2024-06-12</td>
                <td className="px-6 py-4 font-semibold text-xs text-brand-400">3.0 Days</td>
                <td className="px-6 py-4 text-xs text-slate-400">Flu recovery and medical rest</td>
                <td className="px-6 py-4">
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    APPROVED
                  </span>
                </td>
                <td className="px-6 py-4 text-right text-xs text-slate-500">
                  Reviewed by Manager
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
