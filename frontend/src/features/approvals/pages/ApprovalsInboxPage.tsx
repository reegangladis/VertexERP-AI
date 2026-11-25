import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { approvalsApi } from "../api/approvalsApi";
import { UnifiedApprovalItem, WorkflowStats } from "../types";
import { useDemoStore } from "@/lib/demo-store";
import { useAuthStore } from "@/stores/auth-store";
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
} from "lucide-react";

export const ApprovalsInboxPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { fullName } = useAuthStore();
  // Subscribe to demoStore changes so Employee submissions appear live
  useDemoStore();

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
    }) =>
      approvalsApi.processAction(
        entityType,
        entityId,
        action,
        commentText,
        fullName || "Eleanor Vance (Manager)"
      ),
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
        return <Calendar className="w-4 h-4 text-brand-400" />;
      case "REGULARIZATION":
        return <Clock className="w-4 h-4 text-amber-400" />;
      case "QUOTATION":
        return <FileText className="w-4 h-4 text-emerald-400" />;
      default:
        return <DollarSign className="w-4 h-4 text-orange-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-zinc-900/70 border border-zinc-800/90 rounded-2xl p-6 backdrop-blur-xl">
        <span className="text-[11px] font-bold uppercase tracking-widest text-brand-400">
          Governance & Sign-Off Console
        </span>
        <h1 className="text-2xl font-bold text-zinc-50 tracking-tight mt-1">
          Centralized Approvals Inbox
        </h1>
        <p className="text-sm text-zinc-400 mt-0.5">
          Approve or reject employee Leave Requests, Attendance Adjustments, and Commercial Quotes in real time.
        </p>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <StatCard
          title="Total Pending"
          value={stats?.pending_total || 0}
          subtitle="Awaiting authorization"
          icon={<Inbox className="w-5 h-5 text-brand-400" />}
        />
        <StatCard
          title="Pending Leaves"
          value={stats?.pending_leaves || 0}
          subtitle="Employee time-off requests"
          icon={<Calendar className="w-5 h-5 text-amber-400" />}
        />
        <StatCard
          title="Attendance Adjustments"
          value={stats?.pending_regularizations || 0}
          subtitle="Punch corrections"
          icon={<Clock className="w-5 h-5 text-orange-400" />}
        />
        <StatCard
          title="Commercial Quotes"
          value={stats?.pending_quotations || 0}
          subtitle="Sales proposals"
          icon={<FileText className="w-5 h-5 text-emerald-400" />}
        />
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-zinc-800 pb-3">
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
                ? "bg-gradient-to-r from-brand-600 to-amber-600 text-white shadow-md shadow-brand-600/20"
                : "bg-zinc-900 text-zinc-400 border border-zinc-800 hover:bg-zinc-800 hover:text-zinc-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Inbox Items List */}
      <div className="space-y-3">
        {isLoading && (
          <div className="text-center py-12 text-zinc-400 text-sm">Loading approval items...</div>
        )}

        {!isLoading && items.length === 0 && (
          <div className="bg-zinc-900/60 rounded-2xl border border-zinc-800 p-12 text-center space-y-2">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <h3 className="font-bold text-zinc-100 text-base">Inbox Clean!</h3>
            <p className="text-xs text-zinc-400 max-w-sm mx-auto">
              No pending approval requests require your attention in this category.
            </p>
          </div>
        )}

        {items.map((item) => (
          <div
            key={item.id}
            className="bg-zinc-900/75 rounded-2xl border border-zinc-800 p-5 shadow-lg hover:border-brand-500/40 transition flex flex-col md:flex-row md:items-center justify-between gap-4"
          >
            <div className="flex items-start gap-4 flex-1">
              <div className="w-10 h-10 rounded-xl bg-zinc-950 border border-zinc-800 flex items-center justify-center flex-shrink-0 mt-0.5">
                {getCategoryIcon(item.entity_type)}
              </div>

              <div className="space-y-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-bold text-zinc-100 text-sm">{item.title}</span>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      item.priority === "HIGH"
                        ? "bg-rose-500/15 text-rose-300 border border-rose-500/30"
                        : "bg-zinc-800 text-zinc-300 border border-zinc-700"
                    }`}
                  >
                    {item.priority} Priority
                  </span>
                  <StatusBadge status={item.status} />
                </div>

                <div className="text-xs text-zinc-300">{item.summary}</div>

                <div className="text-[11px] text-zinc-400 flex items-center gap-3 pt-1">
                  <span>
                    Requested by: <strong className="text-zinc-200">{item.requester_name}</strong>
                  </span>
                  {item.created_at && <span>Submitted: {formatDate(item.created_at)}</span>}
                  {item.amount && (
                    <span>
                      Amount: <strong className="text-amber-400">{formatCurrency(item.amount)}</strong>
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex items-center gap-2 self-end md:self-center">
              <button
                onClick={() => setSelectedDetails(item)}
                className="px-3 py-1.5 rounded-xl border border-zinc-700 text-xs font-semibold text-zinc-200 hover:bg-zinc-800 transition"
              >
                Inspect
              </button>
              <button
                onClick={() => setActionItem({ item, action: "RETURN" })}
                className="px-3 py-1.5 rounded-xl border border-amber-500/30 bg-amber-500/10 text-amber-300 hover:bg-amber-500/20 text-xs font-semibold transition flex items-center gap-1"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Return</span>
              </button>
              <button
                onClick={() => setActionItem({ item, action: "REJECT" })}
                className="px-3 py-1.5 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300 hover:bg-rose-500/20 text-xs font-semibold transition flex items-center gap-1"
              >
                <XCircle className="w-3.5 h-3.5" />
                <span>Reject</span>
              </button>
              <button
                onClick={() => setActionItem({ item, action: "APPROVE" })}
                className="px-3.5 py-1.5 rounded-xl bg-emerald-600 text-white hover:bg-emerald-500 text-xs font-semibold transition flex items-center gap-1 shadow-md shadow-emerald-950/50"
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
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-zinc-900 rounded-2xl border border-zinc-800 shadow-2xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <h3 className="font-bold text-zinc-100 text-base flex items-center gap-2">
                {actionItem.action === "APPROVE" && <CheckCircle2 className="w-5 h-5 text-emerald-400" />}
                {actionItem.action === "REJECT" && <XCircle className="w-5 h-5 text-rose-400" />}
                {actionItem.action === "RETURN" && <RotateCcw className="w-5 h-5 text-amber-400" />}
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
                className="text-zinc-400 hover:text-zinc-200 text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <div className="space-y-3 text-sm">
              <div className="p-3 bg-zinc-950 rounded-xl border border-zinc-800 text-xs text-zinc-300 space-y-1">
                <div><strong>Item:</strong> {actionItem.item.title}</div>
                <div><strong>Requester:</strong> {actionItem.item.requester_name}</div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-zinc-300 mb-1.5">
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
                  className="w-full px-3 py-2 bg-zinc-950 border rounded-xl border-zinc-800 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-brand-500"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-zinc-800">
              <button
                type="button"
                onClick={() => setActionItem(null)}
                className="px-4 py-2 rounded-xl border border-zinc-700 text-zinc-300 hover:bg-zinc-800 text-xs font-semibold"
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
                    ? "bg-emerald-600 hover:bg-emerald-500"
                    : actionItem.action === "REJECT"
                    ? "bg-rose-600 hover:bg-rose-500"
                    : "bg-amber-600 hover:bg-amber-500"
                }`}
              >
                {actionMutation.isPending ? "Processing..." : `Confirm ${actionItem.action}`}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Details & Approval Timeline Modal */}
      {selectedDetails && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-zinc-900 rounded-2xl border border-zinc-800 shadow-2xl max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <h3 className="font-bold text-zinc-100 text-base">{selectedDetails.title}</h3>
              <button
                onClick={() => setSelectedDetails(null)}
                className="text-zinc-400 hover:text-zinc-200 text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="bg-zinc-950 p-3.5 rounded-xl border border-zinc-800 space-y-2">
                <div className="flex justify-between">
                  <span className="text-zinc-400">Requester:</span>
                  <span className="font-semibold text-zinc-100">{selectedDetails.requester_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-400">Submitted On:</span>
                  <span className="font-semibold text-zinc-200">
                    {selectedDetails.created_at ? formatDate(selectedDetails.created_at) : "N/A"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-400">Current Status:</span>
                  <StatusBadge status={selectedDetails.status} />
                </div>
                <div className="flex justify-between gap-4">
                  <span className="text-zinc-400 shrink-0">Summary:</span>
                  <span className="font-semibold text-zinc-200 text-right">{selectedDetails.summary}</span>
                </div>
              </div>

              <div>
                <h4 className="font-bold text-zinc-200 mb-2">Multi-Level Approval Flow</h4>
                <ApprovalTimeline
                  steps={[
                    {
                      label: "Employee Submission",
                      approver: selectedDetails.requester_name,
                      status: "APPROVED",
                      timestamp: selectedDetails.created_at,
                      comment: "Initial request submitted",
                    },
                    {
                      label: "Managerial Sign-off",
                      approver: fullName || "Department Manager / HR",
                      status: selectedDetails.status === "APPROVED" ? "APPROVED" : "PENDING",
                      comment: "Awaiting manager approval decision",
                    },
                    {
                      label: "Leave Balance & Ledger Sync",
                      approver: "VertexHR Policy Engine",
                      status: selectedDetails.status === "APPROVED" ? "APPROVED" : "PENDING",
                      comment: "Automatically updates remaining quotas upon approval",
                    },
                  ]}
                />
              </div>
            </div>

            <div className="flex justify-end pt-3 border-t border-zinc-800">
              <button
                type="button"
                onClick={() => setSelectedDetails(null)}
                className="px-4 py-2 rounded-xl bg-zinc-800 text-zinc-200 hover:bg-zinc-700 text-xs font-semibold"
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
