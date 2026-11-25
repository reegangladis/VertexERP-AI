import React, { useMemo, useState } from "react";
import { useDemoStore } from "@/lib/demo-store";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { CheckSquare, Plus } from "lucide-react";
import { Link } from "react-router-dom";

export const MyRequestsPage: React.FC = () => {
  const [filterType, setFilterType] = useState("ALL");
  const demoState = useDemoStore();

  const requests = useMemo(() => {
    const leaveItems = demoState.leaveRequests.map((lr) => ({
      id: lr.id,
      type: "LEAVE",
      title: `${lr.leave_type_name} (${lr.total_days} day${lr.total_days === 1 ? "" : "s"})`,
      submittedDate: lr.created_at.split("T")[0],
      approver: lr.approver_name || "Pending Manager Review",
      status: lr.status,
      details: `${lr.start_date} to ${lr.end_date}${lr.remarks ? ` • "${lr.remarks}"` : ""}`,
    }));

    const otherItems = demoState.otherApprovals.map((o) => ({
      id: o.id.toUpperCase(),
      type: o.entity_type,
      title: o.title,
      submittedDate: o.created_at.split("T")[0],
      approver: o.status === "APPROVED" ? "Approved by Leadership" : "Pending Manager Sign-Off",
      status: o.status,
      details: o.summary,
    }));

    return [...leaveItems, ...otherItems];
  }, [demoState.leaveRequests, demoState.otherApprovals]);

  const filtered = requests.filter((r) => (filterType === "ALL" ? true : r.type === filterType));

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-zinc-900/70 border border-zinc-800/80 rounded-2xl p-6">
        <div>
          <h1 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-brand-400" />
            <span>My Requests & Status Tracker</span>
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            Live tracking across all submitted Leaves, Attendance Adjustments, and Approvals.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Filter Tabs */}
          <div className="flex items-center gap-1 bg-zinc-950 border border-zinc-800 rounded-xl p-1 text-xs">
            {["ALL", "LEAVE", "REGULARIZATION", "QUOTATION"].map((t) => (
              <button
                key={t}
                onClick={() => setFilterType(t)}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                  filterType === t
                    ? "bg-brand-600 text-white shadow"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {t === "ALL" ? "All Requests" : t}
              </button>
            ))}
          </div>

          <Link
            to="/ess/leave"
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Leave</span>
          </Link>
        </div>
      </div>

      {/* Requests Table */}
      <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 backdrop-blur-sm p-6 space-y-4">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Request ID</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>Title & Description</TableHead>
              <TableHead>Details & Manager Remarks</TableHead>
              <TableHead>Submitted On</TableHead>
              <TableHead>Assigned Approver</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((item) => (
              <TableRow key={item.id}>
                <TableCell className="font-mono text-xs font-semibold text-brand-400">{item.id}</TableCell>
                <TableCell>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-300 border border-zinc-700">
                    {item.type}
                  </span>
                </TableCell>
                <TableCell className="font-medium text-zinc-100">{item.title}</TableCell>
                <TableCell className="text-xs text-zinc-400 max-w-[260px] truncate" title={item.details}>
                  {item.details}
                </TableCell>
                <TableCell className="text-xs text-zinc-400">{item.submittedDate}</TableCell>
                <TableCell className="text-xs text-zinc-300">{item.approver}</TableCell>
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
