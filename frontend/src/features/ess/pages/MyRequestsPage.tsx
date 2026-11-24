import React, { useState } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { CheckSquare, Clock, Filter } from "lucide-react";

export const MyRequestsPage: React.FC = () => {
  const [filterType, setFilterType] = useState("ALL");

  const requests = [
    {
      id: "REQ-9921",
      type: "LEAVE",
      title: "Casual Leave (2 days)",
      submittedDate: "Nov 23, 2026",
      approver: "Sarah Connor (HR Manager)",
      status: "PENDING",
      details: "Nov 28 - Nov 29, 2026",
    },
    {
      id: "REQ-9884",
      type: "ATTENDANCE_REGULARIZATION",
      title: "Missing Punch Out (Nov 20)",
      submittedDate: "Nov 21, 2026",
      approver: "Sarah Connor (HR Manager)",
      status: "APPROVED",
      details: "Punch corrected to 18:00",
    },
    {
      id: "REQ-9750",
      type: "EXPENSE_REIMBURSEMENT",
      title: "Client Lunch Meeting - Cyberdyne",
      submittedDate: "Nov 15, 2026",
      approver: "Alex Rivera (Finance Manager)",
      status: "APPROVED",
      details: "$145.50 approved for payout",
    },
    {
      id: "REQ-9612",
      type: "LEAVE",
      title: "Earned Leave (4 days)",
      submittedDate: "Oct 01, 2026",
      approver: "Alex Rivera (Department Head)",
      status: "APPROVED",
      details: "Oct 12 - Oct 15, 2026",
    },
  ];

  const filtered = requests.filter((r) => (filterType === "ALL" ? true : r.type === filterType));

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-brand-400" />
            <span>My Requests & Status Tracker</span>
          </h1>
          <p className="text-xs text-slate-400">
            Track all requests submitted by you (Leaves, Attendance Regularizations, Expenses, and Permissions).
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 rounded-lg p-1 text-xs">
          {["ALL", "LEAVE", "ATTENDANCE_REGULARIZATION", "EXPENSE_REIMBURSEMENT"].map((t) => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={`px-3 py-1 rounded-md font-medium transition-colors ${
                filterType === t
                  ? "bg-brand-600 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {t === "ALL" ? "All Requests" : t.replace(/_/g, " ")}
            </button>
          ))}
        </div>
      </div>

      {/* Requests Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur-sm p-6 space-y-4">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Request ID</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>Title & Description</TableHead>
              <TableHead>Details</TableHead>
              <TableHead>Submitted On</TableHead>
              <TableHead>Assigned Approver</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((item) => (
              <TableRow key={item.id}>
                <TableCell className="font-semibold text-slate-200">{item.id}</TableCell>
                <TableCell>
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                    {item.type.replace(/_/g, " ")}
                  </span>
                </TableCell>
                <TableCell className="font-medium text-slate-200">{item.title}</TableCell>
                <TableCell className="text-xs text-slate-400">{item.details}</TableCell>
                <TableCell className="text-xs text-slate-500">{item.submittedDate}</TableCell>
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
