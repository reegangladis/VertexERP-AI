import React, { useEffect, useState } from "react";
import { CalendarOff, Check, X, Clock, CheckCircle2, XCircle, Filter } from "lucide-react";
import { hrApi } from "../api/hrApi";
import { isServerlessDemoMode } from "@/lib/api-client";
import { demoStore, useDemoStore } from "@/lib/demo-store";
import { useAuthStore } from "@/stores/auth-store";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Employee, LeaveRequest, LeaveType } from "../types";

interface NormalizedLeaveRow {
  id: string;
  employeeName: string;
  leaveTypeName: string;
  startDate: string;
  endDate: string;
  totalDays: number;
  reason: string;
  status: string;
  approverRemarks?: string | null;
}

export const LeaveManagementPage: React.FC = () => {
  const { fullName } = useAuthStore();
  const demoState = useDemoStore();
  const [backendRequests, setBackendRequests] = useState<LeaveRequest[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [leaveTypes, setLeaveTypes] = useState<LeaveType[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);
  const [feedbackToast, setFeedbackToast] = useState<string | null>(null);

  const loadLeaves = async () => {
    try {
      const [tRes, rRes, eRes] = await Promise.allSettled([
        hrApi.getLeaveTypes(),
        hrApi.getLeaveRequests(),
        hrApi.getEmployees(),
      ]);
      if (tRes.status === "fulfilled" && !isServerlessDemoMode()) setLeaveTypes(tRes.value);
      if (rRes.status === "fulfilled" && !isServerlessDemoMode()) setBackendRequests(rRes.value);
      if (eRes.status === "fulfilled" && !isServerlessDemoMode()) setEmployees(eRes.value);
    } catch {
      // handled cleanly via demoStore fallback
    }
  };

  useEffect(() => {
    loadLeaves();
  }, []);

  // Merge backend requests if live FastAPI returned them; otherwise show rich reactive demoStore rows
  const rows: NormalizedLeaveRow[] = React.useMemo(() => {
    if (backendRequests.length > 0 && !isServerlessDemoMode()) {
      return backendRequests.map((req) => {
        const emp = employees.find((e) => e.id === req.employee_id);
        const lt = leaveTypes.find((t) => t.id === req.leave_type_id);
        return {
          id: req.id,
          employeeName: emp ? `${emp.first_name} ${emp.last_name}` : "Employee",
          leaveTypeName: lt?.name || "Paid Leave",
          startDate: req.start_date,
          endDate: req.end_date,
          totalDays: Number(req.total_days),
          reason: req.reason,
          status: req.status,
          approverRemarks: req.remarks,
        };
      });
    }

    return demoState.leaveRequests.map((lr) => ({
      id: lr.id,
      employeeName: lr.employee_name,
      leaveTypeName: lr.leave_type_name,
      startDate: lr.start_date,
      endDate: lr.end_date,
      totalDays: lr.total_days,
      reason: lr.reason,
      status: lr.status,
      approverRemarks: lr.remarks,
    }));
  }, [backendRequests, employees, leaveTypes, demoState.leaveRequests]);

  const filteredRows = rows.filter((r) => {
    if (statusFilter === "PENDING") return r.status === "SUBMITTED" || r.status === "PENDING";
    if (statusFilter === "APPROVED") return r.status === "APPROVED";
    if (statusFilter === "REJECTED") return r.status === "REJECTED";
    return true;
  });

  const handleReview = async (row: NormalizedLeaveRow, decision: "APPROVED" | "REJECTED") => {
    setActionLoadingId(row.id);
    const remarks =
      decision === "APPROVED"
        ? `Approved by ${fullName || "HR Manager"} via Leave Governance.`
        : `Declined by ${fullName || "HR Manager"} due to team coverage.`;

    try {
      await hrApi.reviewLeave(row.id, { status: decision, remarks });
    } catch {
      // Fall back smoothly when running serverless/offline
    }

    demoStore.reviewLeave({
      requestId: row.id,
      action: decision === "APPROVED" ? "APPROVE" : "REJECT",
      reviewerName: fullName || "Eleanor Vance (HR Manager)",
      remarks,
    });

    await loadLeaves();
    setActionLoadingId(null);
    setFeedbackToast(`${row.employeeName}'s leave (${row.totalDays}d) marked ${decision}.`);
    setTimeout(() => setFeedbackToast(null), 3500);
  };

  const pendingCount = rows.filter((r) => r.status === "SUBMITTED" || r.status === "PENDING").length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-zinc-900/70 border border-zinc-800 rounded-2xl p-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <CalendarOff className="w-6 h-6 text-brand-400" />
            Leave Management & Entitlements
          </h1>
          <p className="text-zinc-400 text-sm mt-0.5">
            Annual leave quotas, policy rules, and real-time manager approval governance queue.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-zinc-950 border border-zinc-800 rounded-xl p-1 text-xs">
          {[
            { key: "ALL", label: `All (${rows.length})` },
            { key: "PENDING", label: `Pending (${pendingCount})` },
            { key: "APPROVED", label: "Approved" },
            { key: "REJECTED", label: "Rejected" },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setStatusFilter(tab.key)}
              className={`px-3 py-1.5 rounded-lg font-semibold transition ${
                statusFilter === tab.key
                  ? "bg-brand-600 text-white shadow"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {feedbackToast && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{feedbackToast}</span>
        </div>
      )}

      {/* Leave Quota Policy Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-2xl bg-zinc-900/70 border border-zinc-800 hover:border-brand-500/30 transition">
          <div className="text-xs font-medium text-zinc-400">Annual Paid Leave</div>
          <div className="text-2xl font-bold text-white mt-1">20.0 Days</div>
          <div className="text-xs text-zinc-500 mt-1">Accrual: Monthly &bull; Max Carry: 5 Days</div>
        </div>
        <div className="p-5 rounded-2xl bg-zinc-900/70 border border-zinc-800 hover:border-emerald-500/30 transition">
          <div className="text-xs font-medium text-zinc-400">Sick & Medical Leave</div>
          <div className="text-2xl font-bold text-white mt-1">10.0 Days</div>
          <div className="text-xs text-zinc-500 mt-1">Accrual: Annual Quota &bull; Paid</div>
        </div>
        <div className="p-5 rounded-2xl bg-zinc-900/70 border border-zinc-800 hover:border-amber-500/30 transition">
          <div className="text-xs font-medium text-zinc-400">Parental / Maternity Leave</div>
          <div className="text-2xl font-bold text-white mt-1">90.0 Days</div>
          <div className="text-xs text-zinc-500 mt-1">Statutory Standard &bull; 100% Paid</div>
        </div>
      </div>

      {/* Manager Approval Queue Table */}
      <div className="rounded-2xl bg-zinc-900/70 border border-zinc-800 overflow-hidden shadow-xl">
        <div className="px-6 py-4 border-b border-zinc-800 flex items-center justify-between">
          <span className="font-semibold text-sm text-zinc-100">
            Manager Leave Approval Queue
          </span>
          {pendingCount > 0 && (
            <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30">
              {pendingCount} Pending Sign-Off
            </span>
          )}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-zinc-950/60 text-zinc-400 uppercase text-[11px] font-semibold tracking-wider border-b border-zinc-800">
              <tr>
                <th className="px-6 py-3.5">Employee</th>
                <th className="px-6 py-3.5">Leave Type</th>
                <th className="px-6 py-3.5">Dates</th>
                <th className="px-6 py-3.5">Days</th>
                <th className="px-6 py-3.5">Reason</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5 text-right">Manager Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/70 text-zinc-300">
              {filteredRows.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-10 text-center text-xs text-zinc-500">
                    No leave requests found in this filter view.
                  </td>
                </tr>
              ) : (
                filteredRows.map((row) => {
                  const isPending = row.status === "SUBMITTED" || row.status === "PENDING";
                  const isBusy = actionLoadingId === row.id;
                  return (
                    <tr key={row.id} className="hover:bg-zinc-800/40 transition-colors">
                      <td className="px-6 py-4 text-xs font-semibold text-zinc-100">{row.employeeName}</td>
                      <td className="px-6 py-4 text-xs text-zinc-300">{row.leaveTypeName}</td>
                      <td className="px-6 py-4 text-xs font-medium text-zinc-200">
                        {row.startDate} to {row.endDate}
                      </td>
                      <td className="px-6 py-4 font-bold text-xs text-brand-400">
                        {row.totalDays.toFixed(1)} Days
                      </td>
                      <td className="px-6 py-4 text-xs text-zinc-400 max-w-[240px] truncate" title={row.reason}>
                        {row.reason}
                      </td>
                      <td className="px-6 py-4">
                        <StatusBadge status={row.status} />
                      </td>
                      <td className="px-6 py-4 text-right text-xs">
                        {isPending ? (
                          <div className="inline-flex items-center gap-2">
                            <button
                              type="button"
                              disabled={isBusy}
                              onClick={() => handleReview(row, "REJECTED")}
                              className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-rose-500/15 text-rose-300 hover:bg-rose-500/25 border border-rose-500/30 font-semibold transition disabled:opacity-50"
                            >
                              <X className="w-3.5 h-3.5" /> Reject
                            </button>
                            <button
                              type="button"
                              disabled={isBusy}
                              onClick={() => handleReview(row, "APPROVED")}
                              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold transition shadow-sm disabled:opacity-50"
                            >
                              <Check className="w-3.5 h-3.5" /> Approve
                            </button>
                          </div>
                        ) : (
                          <span className="text-zinc-500 text-[11px] italic">
                            {row.approverRemarks || "Reviewed by Manager"}
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
