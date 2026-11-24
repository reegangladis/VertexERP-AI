import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { approvalsApi } from "../api/approvalsApi";
import { UnifiedApprovalItem, WorkflowStats } from "../types";
import { StatCard } from "@/components/ui/StatCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { ApprovalTimeline } from "@/components/ui/ApprovalTimeline";
import { formatDate, formatCurrency } from "@/lib/utils";
import {
  Inbox,
  CheckCircle2,
  XCircle,
  RotateCcw,
  Calendar,
  Clock,
  FileText,
  DollarSign,
  AlertCircle,
  Filter,
} from "lucide-react";

export const ApprovalsInboxPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [activeCategory, setActiveCategory] = useState<string>("ALL");
  const [actionItem, setActionItem] = useState<{
    item: UnifiedApprovalItem;
    action: "APPROVE" | "REJECT" | "RETURN";
  } | null>(null);
  const [comments, setComments] = useState("");
  const [selectedDetails, setSelectedDetails] = useState<UnifiedApprovalItem | null>(null);

  const { data: stats } = useQuery<WorkflowStats>({
    queryKey: ["workflow-stats"],
    queryFn: approvalsApi.getStats,
  });

  const { data: items = [], isLoading } = useQuery<UnifiedApprovalItem[]>({
    queryKey: ["workflow-inbox", activeCategory],
    queryFn: () => approvalsApi.getInbox(activeCategory === "ALL" ? undefined : activeCategory),
  });

  const actionMutation = useMutation({
    mutationFn: ({
      entityType,
      entityId,
      action,
      commentText,
    }: {
      entityType: string;
      entityId: string;
      action: "APPROVE" | "REJECT" | "RETURN";
      commentText?: string;
    }) => approvalsApi.processAction(entityType, entityId, action, commentText),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflow-inbox"] });
      queryClient.invalidateQueries({ queryKey: ["workflow-stats"] });
      setActionItem(null);
      setComments("");
      setSelectedDetails(null);
    },
  });

  const handleConfirmAction = () => {
    if (!actionItem) return;
    actionMutation.mutate({
      entityType: actionItem.item.entity_type,
      entityId: actionItem.item.entity_id,
      action: actionItem.action,
      commentText: comments,
    });
  };

  const getCategoryIcon = (type: string) => {
    switch (type) {
      case "LEAVE":
        return <Calendar className="w-4 h-4 text-indigo-600" />;
      case "REGULARIZATION":
        return <Clock className="w-4 h-4 text-purple-600" />;
      case "QUOTATION":
        return <FileText className="w-4 h-4 text-emerald-600" />;
      default:
        return <DollarSign className="w-4 h-4 text-blue-600" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Centralized Approvals Inbox</h1>
        <p className="text-sm text-slate-500">
          Unified governance center for managerial sign-offs across HR, CRM, and Finance.
        </p>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <StatCard
          title="Total Pending"
          value={stats?.pending_total || 0}
          subtitle="Awaiting authorization"
          icon={<Inbox className="w-5 h-5 text-indigo-600" />}
        />
        <StatCard
          title="Pending Leaves"
          value={stats?.pending_leaves || 0}
          subtitle="Time off requests"
          icon={<Calendar className="w-5 h-5 text-purple-600" />}
        />
        <StatCard
          title="Attendance Adjustments"
          value={stats?.pending_regularizations || 0}
          subtitle="Punch corrections"
          icon={<Clock className="w-5 h-5 text-amber-600" />}
        />
        <StatCard
          title="Commercial Quotes"
          value={stats?.pending_quotations || 0}
          subtitle="Sales proposals"
          icon={<FileText className="w-5 h-5 text-emerald-600" />}
        />
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 pb-3">
        {[
          { key: "ALL", label: "All Pending" },
          { key: "LEAVE", label: "Leave Requests" },
          { key: "REGULARIZATION", label: "Attendance Adjustments" },
          { key: "QUOTATION", label: "Sales Quotes" },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveCategory(tab.key)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
              activeCategory === tab.key
                ? "bg-indigo-600 text-white shadow-sm"
                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Inbox Items List */}
      <div className="space-y-3">
        {isLoading && (
          <div className="text-center py-12 text-slate-400 text-sm">Loading approval items...</div>
        )}

        {!isLoading && items.length === 0 && (
          <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-2">
            <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto" />
            <h3 className="font-bold text-slate-800 text-base">Inbox Clean!</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              No pending approval requests require your attention in this category.
            </p>
          </div>
        )}

        {items.map((item) => (
          <div
            key={item.id}
            className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm hover:border-indigo-200 transition flex flex-col md:flex-row md:items-center justify-between gap-4"
          >
            <div className="flex items-start gap-4 flex-1">
              <div className="w-10 h-10 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-center flex-shrink-0 mt-0.5">
                {getCategoryIcon(item.entity_type)}
              </div>

              <div className="space-y-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-bold text-slate-900 text-sm">{item.title}</span>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      item.priority === "HIGH"
                        ? "bg-rose-50 text-rose-700 border border-rose-200"
                        : "bg-slate-100 text-slate-600"
                    }`}
                  >
                    {item.priority} Priority
                  </span>
                  <StatusBadge status={item.status} />
                </div>

                <div className="text-xs text-slate-600">{item.summary}</div>

                <div className="text-[11px] text-slate-400 flex items-center gap-3 pt-1">
                  <span>Requested by: <strong className="text-slate-700">{item.requester_name}</strong></span>
                  {item.created_at && (
                    <span>Submitted: {formatDate(item.created_at)}</span>
                  )}
                  {item.amount && (
                    <span>Amount: <strong className="text-slate-800">{formatCurrency(item.amount)}</strong></span>
                  )}
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex items-center gap-2 self-end md:self-center">
              <button
                onClick={() => setSelectedDetails(item)}
                className="px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
              >
                Inspect
              </button>
              <button
                onClick={() => setActionItem({ item, action: "RETURN" })}
                className="px-3 py-1.5 rounded-xl border border-amber-200 bg-amber-50 text-amber-700 hover:bg-amber-100 text-xs font-semibold transition flex items-center gap-1"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Return</span>
              </button>
              <button
                onClick={() => setActionItem({ item, action: "REJECT" })}
                className="px-3 py-1.5 rounded-xl border border-rose-200 bg-rose-50 text-rose-700 hover:bg-rose-100 text-xs font-semibold transition flex items-center gap-1"
              >
                <XCircle className="w-3.5 h-3.5" />
                <span>Reject</span>
              </button>
              <button
                onClick={() => setActionItem({ item, action: "APPROVE" })}
                className="px-3.5 py-1.5 rounded-xl bg-emerald-600 text-white hover:bg-emerald-700 text-xs font-semibold transition flex items-center gap-1 shadow-sm"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Approve</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Action Confirmation Modal */}
      {actionItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
                {actionItem.action === "APPROVE" && <CheckCircle2 className="w-5 h-5 text-emerald-600" />}
                {actionItem.action === "REJECT" && <XCircle className="w-5 h-5 text-rose-600" />}
                {actionItem.action === "RETURN" && <RotateCcw className="w-5 h-5 text-amber-600" />}
                <span>
                  {actionItem.action === "APPROVE"
                    ? "Confirm Approval"
                    : actionItem.action === "REJECT"
                    ? "Confirm Rejection"
                    : "Return for Revision"}
                </span>
              </h3>
              <button
                onClick={() => setActionItem(null)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <div className="space-y-3 text-sm">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs text-slate-700">
                <strong>Item:</strong> {actionItem.item.title}
                <br />
                <strong>Requester:</strong> {actionItem.item.requester_name}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">
                  {actionItem.action === "APPROVE" ? "Remarks (Optional)" : "Reason / Feedback *"}
                </label>
                <textarea
                  rows={3}
                  value={comments}
                  onChange={(e) => setComments(e.target.value)}
                  placeholder={
                    actionItem.action === "APPROVE"
                      ? "Approved in accordance with company policy."
                      : "Please specify why this request cannot be approved as submitted..."
                  }
                  className="w-full px-3 py-2 border rounded-xl border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setActionItem(null)}
                className="px-4 py-2 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmAction}
                disabled={
                  (actionItem.action !== "APPROVE" && !comments.trim()) ||
                  actionMutation.isPending
                }
                className={`px-4 py-2 rounded-xl text-xs font-semibold text-white transition disabled:opacity-50 ${
                  actionItem.action === "APPROVE"
                    ? "bg-emerald-600 hover:bg-emerald-700"
                    : actionItem.action === "REJECT"
                    ? "bg-rose-600 hover:bg-rose-700"
                    : "bg-amber-600 hover:bg-amber-700"
                }`}
              >
                {actionMutation.isPending
                  ? "Processing..."
                  : `Confirm ${actionItem.action}`}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Details & Approval Timeline Modal */}
      {selectedDetails && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-base">{selectedDetails.title}</h3>
              <button
                onClick={() => setSelectedDetails(null)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-100 space-y-2">
                <div className="flex justify-between">
                  <span className="text-slate-500">Requester:</span>
                  <span className="font-semibold text-slate-800">{selectedDetails.requester_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Submitted On:</span>
                  <span className="font-semibold text-slate-800">
                    {selectedDetails.created_at ? formatDate(selectedDetails.created_at) : "N/A"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Current Status:</span>
                  <StatusBadge status={selectedDetails.status} />
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Summary:</span>
                  <span className="font-semibold text-slate-800 text-right">{selectedDetails.summary}</span>
                </div>
              </div>

              <div>
                <h4 className="font-bold text-slate-800 mb-2">Multi-Level Approval Flow</h4>
                <ApprovalTimeline
                  steps={[
                    {
                      label: "Employee Submission",
                      approver: selectedDetails.requester_name,
                      status: "APPROVED",
                      timestamp: selectedDetails.created_at,
                      comment: "Initial submission",
                    },
                    {
                      label: "Managerial Sign-off",
                      approver: "Department Manager / HR",
                      status: selectedDetails.status === "APPROVED" ? "APPROVED" : "PENDING",
                      comment: "Pending executive review",
                    },
                    {
                      label: "System Execution",
                      approver: "Automated Ledger Engine",
                      status: selectedDetails.status === "APPROVED" ? "APPROVED" : "PENDING",
                      comment: "Will post to payroll/ledger automatically upon final sign-off",
                    },
                  ]}
                />
              </div>
            </div>

            <div className="flex justify-end pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setSelectedDetails(null)}
                className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 text-xs font-semibold"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
