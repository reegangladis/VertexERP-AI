import React, { useState } from "react";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table";
import { Palmtree, Plus, Calendar, Clock, CheckCircle2 } from "lucide-react";

export const ApplyLeavePage: React.FC = () => {
  const [isApplyOpen, setIsApplyOpen] = useState(false);
  const [leaveType, setLeaveType] = useState("CL");
  const [startDate, setStartDate] = useState("2026-11-28");
  const [endDate, setEndDate] = useState("2026-11-29");
  const [reason, setReason] = useState("");
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const leaveBalances = [
    { code: "CL", name: "Casual Leave", total: 12.0, used: 3.5, balance: 8.5, color: "text-blue-400" },
    { code: "SL", name: "Sick Leave", total: 10.0, used: 0.0, balance: 10.0, color: "text-emerald-400" },
    { code: "EL", name: "Earned / Privilege Leave", total: 18.0, used: 4.0, balance: 14.0, color: "text-purple-400" },
    { code: "CO", name: "Compensatory Off", total: 2.0, used: 1.0, balance: 1.0, color: "text-amber-400" },
  ];

  const [leaveHistory, setLeaveHistory] = useState([
    {
      id: "LR-001",
      leaveType: "Casual Leave",
      dates: "Nov 18, 2026 - Nov 18, 2026",
      days: 1.0,
      reason: "Family personal commitment",
      appliedAt: "2026-11-15",
      status: "APPROVED",
      approver: "Sarah Connor (HR Manager)",
    },
    {
      id: "LR-002",
      leaveType: "Earned Leave",
      dates: "Oct 12, 2026 - Oct 15, 2026",
      days: 4.0,
      reason: "Annual vacation trip",
      appliedAt: "2026-10-01",
      status: "APPROVED",
      approver: "Alex Rivera (Department Head)",
    },
  ]);

  const handleApply = (e: React.FormEvent) => {
    e.preventDefault();
    const newEntry = {
      id: `LR-00${leaveHistory.length + 1}`,
      leaveType: leaveBalances.find((b) => b.code === leaveType)?.name || "Casual Leave",
      dates: `${startDate} - ${endDate}`,
      days: 2.0,
      reason: reason,
      appliedAt: new Date().toISOString().split("T")[0],
      status: "PENDING",
      approver: "Pending Manager Review",
    };
    setLeaveHistory([newEntry, ...leaveHistory]);
    setSuccessMsg("Leave application submitted successfully for manager approval.");
    setTimeout(() => {
      setIsApplyOpen(false);
      setSuccessMsg(null);
      setReason("");
    }, 1500);
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Palmtree className="w-5 h-5 text-brand-400" />
            <span>Leave Management & Applications</span>
          </h1>
          <p className="text-xs text-slate-400">
            Review your annual leave balances, submit vacation requests, and track approval status.
          </p>
        </div>

        <Button
          variant="primary"
          onClick={() => setIsApplyOpen(true)}
          className="text-xs font-semibold flex items-center gap-1.5"
        >
          <Plus className="w-4 h-4" />
          <span>Apply for Leave</span>
        </Button>
      </div>

      {/* Quota Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {leaveBalances.map((b) => (
          <div
            key={b.code}
            className="p-5 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-2"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400">{b.name}</span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                {b.code}
              </span>
            </div>
            <div className="text-3xl font-bold text-slate-100">{b.balance.toFixed(1)}</div>
            <div className="text-[11px] text-slate-500">
              Used: {b.used.toFixed(1)} / Total: {b.total.toFixed(1)}
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-brand-500 h-full rounded-full"
                style={{ width: `${(b.balance / b.total) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Leave Application Modal */}
      {isApplyOpen && (
        <div className="p-6 rounded-2xl border border-brand-500/40 bg-slate-900/95 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-slate-100">Submit New Leave Request</h3>
            <button
              onClick={() => setIsApplyOpen(false)}
              className="text-xs text-slate-400 hover:text-slate-200"
            >
              Cancel
            </button>
          </div>

          {successMsg ? (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              <span>{successMsg}</span>
            </div>
          ) : (
            <form onSubmit={handleApply} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Select
                  label="Leave Category"
                  value={leaveType}
                  onChange={(e) => setLeaveType(e.target.value)}
                  options={leaveBalances.map((b) => ({
                    value: b.code,
                    label: `${b.name} (${b.balance} days left)`,
                  }))}
                />
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

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Reason for Leave
                </label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="Provide context for your manager (e.g., attending doctor consultation or family function)"
                  required
                  rows={3}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-100 focus:outline-none focus:border-brand-500"
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
                <Button type="submit" variant="primary" className="text-xs font-semibold">
                  Send for Approval
                </Button>
              </div>
            </form>
          )}
        </div>
      )}

      {/* History Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur-sm p-6 space-y-4">
        <h3 className="text-sm font-bold text-slate-100">Leave Request History</h3>
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
                <TableCell className="font-semibold text-slate-200">{item.id}</TableCell>
                <TableCell>{item.leaveType}</TableCell>
                <TableCell>{item.dates}</TableCell>
                <TableCell className="font-semibold text-brand-400">{item.days}</TableCell>
                <TableCell className="max-w-[200px] truncate">{item.reason}</TableCell>
                <TableCell className="text-xs text-slate-400">{item.approver}</TableCell>
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
