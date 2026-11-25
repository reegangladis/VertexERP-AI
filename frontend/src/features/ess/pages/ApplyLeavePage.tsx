import React, { useMemo, useState } from "react";
import { useAuthStore } from "@/stores/auth-store";
import { useDemoStore, demoStore } from "@/lib/demo-store";
import { apiClient, isServerlessDemoMode } from "@/lib/api-client";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table";
import { Palmtree, Plus, CheckCircle2, Clock, Sparkles, CalendarDays, Send } from "lucide-react";

export const ApplyLeavePage: React.FC = () => {
  const { userId, fullName, email } = useAuthStore();
  const demoState = useDemoStore();

  const [isApplyOpen, setIsApplyOpen] = useState(false);
  const [leaveType, setLeaveType] = useState("CL");
  const [startDate, setStartDate] = useState("2026-12-08");
  const [endDate, setEndDate] = useState("2026-12-09");
  const [reason, setReason] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Compute number of calendar/working days between dates cleanly
  const calculatedDays = useMemo(() => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime()) || end < start) return 0;
    const diff = Math.round((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1;
    return Math.max(1, diff);
  }, [startDate, endDate]);

  const leaveBalances = demoState.leaveBalances;
  const leaveHistory = useMemo(() => {
    const targetEmail = (email || "employee@vertexerp.com").toLowerCase();
    // Show current user's requests (or Alex Morgan's demo history when previewing ESS)
    const mine = demoState.leaveRequests.filter(
      (r) => r.employee_email.toLowerCase() === targetEmail || targetEmail === "admin@vertexerp.com"
    );
    return mine.length > 0 ? mine : demoState.leaveRequests;
  }, [demoState.leaveRequests, email]);

  const handleApply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (calculatedDays <= 0) {
      setErrorMsg("End date must be on or after the start date.");
      return;
    }
    setIsSubmitting(true);
    setErrorMsg(null);

    let backendCreatedId: string | undefined;
    try {
      // Attempt real backend submission if running against FastAPI
      const types = await apiClient<Array<{ id: string; code: string; name: string }>>("/hr/leaves/types");
      if (!isServerlessDemoMode() && Array.isArray(types) && types.length > 0) {
        const matchedType =
          types.find((t) => t.code.toUpperCase().startsWith(leaveType.charAt(0))) || types[0];
        const created = await apiClient<{ id: string }>("/hr/leaves/requests", {
          method: "POST",
          body: JSON.stringify({
            employee_id: userId || "16d9128a-2059-4647-9358-32b683c1a16c",
            leave_type_id: matchedType.id,
            start_date: startDate,
            end_date: endDate,
            total_days: calculatedDays,
            reason: reason.trim(),
          }),
        });
        backendCreatedId = created?.id;
      }
    } catch {
      // Offline / serverless mode cleanly handled by shared interactive demoStore
    }

    demoStore.applyLeave({
      overrideId: backendCreatedId,
      employeeId: userId || "9d6bcc63-5acf-471e-afac-18d4b7386ee6",
      employeeName: fullName || "Alex Morgan",
      employeeEmail: email || "employee@vertexerp.com",
      leaveTypeCode: leaveType,
      startDate,
      endDate,
      totalDays: calculatedDays,
      reason: reason.trim(),
    });

    setIsSubmitting(false);
    setSuccessMsg(
      `Leave request (${calculatedDays} day${calculatedDays > 1 ? "s" : ""}) submitted and routed to your Manager's Approvals Inbox.`
    );
    setTimeout(() => {
      setIsApplyOpen(false);
      setSuccessMsg(null);
      setReason("");
    }, 1800);
  };

  const accentBarColors: Record<string, string> = {
    CL: "from-orange-500 to-amber-500",
    SL: "from-emerald-500 to-green-500",
    EL: "from-amber-500 to-yellow-500",
    CO: "from-rose-500 to-pink-500",
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-zinc-900/70 border border-zinc-800/80 rounded-2xl p-6 backdrop-blur-xl">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-widest text-brand-400">
            Time-Off & Approval Workflow
          </span>
          <h1 className="text-2xl font-bold text-zinc-50 flex items-center gap-2.5 mt-1">
            <Palmtree className="w-6 h-6 text-brand-400" />
            <span>Leave Management & Applications</span>
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            Monitor annual leave quotas, submit requests directly to your reporting manager, and track approval decisions live.
          </p>
        </div>

        <Button
          variant="primary"
          onClick={() => setIsApplyOpen(true)}
          className="text-xs font-semibold flex items-center gap-2 shadow-lg shadow-brand-600/25"
        >
          <Plus className="w-4 h-4" />
          <span>Apply for Leave</span>
        </Button>
      </div>

      {/* Quota Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {leaveBalances.map((b) => {
          const pct = b.total > 0 ? Math.min(100, Math.max(0, (b.balance / b.total) * 100)) : 0;
          return (
            <div
              key={b.code}
              className="p-5 rounded-2xl border border-zinc-800/90 bg-zinc-900/70 backdrop-blur-sm space-y-3 hover:border-brand-500/40 transition-all group"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-zinc-300">{b.name}</span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-zinc-800 text-brand-300 border border-zinc-700">
                  {b.code}
                </span>
              </div>
              <div className="flex items-baseline gap-2">
                <div className="text-3xl font-bold text-white">{b.balance.toFixed(1)}</div>
                <span className="text-xs text-zinc-400">days available</span>
              </div>
              <div className="flex items-center justify-between text-[11px] text-zinc-400">
                <span>Used: <strong className="text-zinc-200">{b.used.toFixed(1)}</strong></span>
                {b.pending > 0 && (
                  <span className="text-amber-400 font-semibold">Pending: {b.pending.toFixed(1)}d</span>
                )}
                <span>Total: {b.total.toFixed(1)}</span>
              </div>
              <div className="w-full bg-zinc-800 h-2 rounded-full overflow-hidden">
                <div
                  className={`bg-gradient-to-r ${accentBarColors[b.code] || "from-brand-500 to-amber-500"} h-full rounded-full transition-all duration-500`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Leave Application Panel */}
      {isApplyOpen && (
        <div className="p-6 rounded-2xl border border-brand-500/40 bg-zinc-900/95 backdrop-blur-xl shadow-2xl space-y-5">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-brand-500/15 border border-brand-500/30">
                <Send className="w-4 h-4 text-brand-400" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-zinc-100">Submit New Leave Request</h3>
                <p className="text-[11px] text-zinc-400">Routes instantaneously to Manager Approvals Inbox & HR Leave Governance</p>
              </div>
            </div>
            <button
              onClick={() => setIsApplyOpen(false)}
              className="text-xs text-zinc-400 hover:text-zinc-200 px-2.5 py-1 rounded-lg hover:bg-zinc-800"
            >
              Close
            </button>
          </div>

          {errorMsg && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
              {errorMsg}
            </div>
          )}

          {successMsg ? (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2.5">
              <CheckCircle2 className="w-5 h-5 shrink-0" />
              <div>
                <div className="font-bold">Submitted for Managerial Review</div>
                <div className="text-emerald-200/80 mt-0.5">{successMsg}</div>
              </div>
            </div>
          ) : (
            <form onSubmit={handleApply} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-end">
                <div className="sm:col-span-2">
                  <Select
                    label="Leave Category"
                    value={leaveType}
                    onChange={(e) => setLeaveType(e.target.value)}
                    options={leaveBalances.map((b) => ({
                      value: b.code,
                      label: `${b.name} (${b.balance.toFixed(1)} days available)`,
                    }))}
                  />
                </div>
                <Input
                  label="Start Date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  required
                />
                <Input
                  label="End Date"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  required
                />
              </div>

              <div className="flex items-center justify-between px-4 py-2.5 rounded-xl bg-zinc-950/70 border border-zinc-800 text-xs">
                <span className="text-zinc-400 flex items-center gap-2">
                  <CalendarDays className="w-4 h-4 text-brand-400" />
                  Calculated Leave Duration:
                </span>
                <span className="font-bold text-brand-400 text-sm">
                  {calculatedDays} Day{calculatedDays === 1 ? "" : "s"}
                </span>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-zinc-300 mb-1.5">
                  Reason for Leave <span className="text-rose-400">*</span>
                </label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="Provide context for your manager (e.g., family travel, medical consultation, personal errand)"
                  required
                  rows={3}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-xl p-3 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setIsApplyOpen(false)}
                  className="text-xs"
                >
                  Cancel
                </Button>
                <Button type="submit" variant="primary" isLoading={isSubmitting} className="text-xs font-semibold">
                  Send for Manager Approval
                </Button>
              </div>
            </form>
          )}
        </div>
      )}

      {/* History Table */}
      <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 backdrop-blur-sm p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-zinc-100 flex items-center gap-2">
              <Clock className="w-4 h-4 text-brand-400" />
              <span>Leave Request History & Approval Status</span>
            </h3>
            <p className="text-[11px] text-zinc-400 mt-0.5">
              Real-time status synced with Manager Approvals Inbox & HR Governance.
            </p>
          </div>
          <span className="text-[11px] px-2.5 py-1 rounded-full bg-zinc-800 text-zinc-300 font-semibold border border-zinc-700">
            {leaveHistory.length} Request{leaveHistory.length === 1 ? "" : "s"}
          </span>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Request ID</TableHead>
              <TableHead>Leave Type</TableHead>
              <TableHead>Date Range</TableHead>
              <TableHead>Days</TableHead>
              <TableHead>Reason</TableHead>
              <TableHead>Approver / Remarks</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {leaveHistory.map((item) => (
              <TableRow key={item.id}>
                <TableCell className="font-mono text-xs font-semibold text-brand-400">{item.id}</TableCell>
                <TableCell className="font-medium text-zinc-200">{item.leave_type_name}</TableCell>
                <TableCell className="text-xs text-zinc-300">
                  {item.start_date} &rarr; {item.end_date}
                </TableCell>
                <TableCell className="font-bold text-amber-400">{item.total_days.toFixed(1)}</TableCell>
                <TableCell className="max-w-[220px] truncate text-xs text-zinc-300" title={item.reason}>
                  {item.reason}
                </TableCell>
                <TableCell className="text-xs text-zinc-400">
                  {item.approver_name ? (
                    <div>
                      <div className="font-medium text-zinc-200">{item.approver_name}</div>
                      {item.remarks && <div className="text-[11px] text-zinc-400 italic truncate max-w-[200px]">"{item.remarks}"</div>}
                    </div>
                  ) : (
                    <span className="text-amber-400/90 flex items-center gap-1">
                      <Sparkles className="w-3 h-3" /> Pending Manager Review
                    </span>
                  )}
                </TableCell>
                <TableCell>
                  <StatusBadge status={item.status} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
