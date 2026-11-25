import { apiClient, isServerlessDemoMode } from "@/lib/api-client";
import { demoStore } from "@/lib/demo-store";
import { UnifiedApprovalItem, WorkflowStats } from "../types";

function buildDemoInboxItems(category?: string): UnifiedApprovalItem[] {
  const state = demoStore.getState();
  const items: UnifiedApprovalItem[] = [];

  if (!category || category === "LEAVE") {
    state.leaveRequests
      .filter((lr) => lr.status === "SUBMITTED" || lr.status === "PENDING")
      .forEach((lr) => {
        items.push({
          id: lr.id,
          entity_type: "LEAVE",
          entity_id: lr.id,
          requester_name: lr.employee_name,
          requester_email: lr.employee_email,
          title: `${lr.leave_type_name}: ${lr.total_days} Day(s)`,
          summary: `${lr.start_date} to ${lr.end_date} — ${lr.reason}`,
          status: lr.status,
          priority: lr.total_days >= 3 ? "HIGH" : "MEDIUM",
          created_at: lr.created_at,
          details: {
            start_date: lr.start_date,
            end_date: lr.end_date,
            total_days: lr.total_days,
            leave_type: lr.leave_type_name,
            reason: lr.reason,
          },
        });
      });
  }

  state.otherApprovals
    .filter((o) => (!category || o.entity_type === category) && (o.status === "PENDING" || o.status === "PENDING_APPROVAL"))
    .forEach((o) => {
      items.push({
        id: o.id,
        entity_type: o.entity_type,
        entity_id: o.entity_id,
        requester_name: o.requester_name,
        requester_email: o.requester_email,
        title: o.title,
        summary: o.summary,
        amount: o.amount,
        currency: o.currency,
        status: o.status,
        priority: o.priority,
        created_at: o.created_at,
        details: o.details,
      });
    });

  return items;
}

function buildDemoStats(): WorkflowStats {
  const state = demoStore.getState();
  const pendingLeaves = state.leaveRequests.filter(
    (l) => l.status === "SUBMITTED" || l.status === "PENDING"
  ).length;
  const approvedLeaves = state.leaveRequests.filter((l) => l.status === "APPROVED").length;
  const rejectedLeaves = state.leaveRequests.filter((l) => l.status === "REJECTED").length;

  const pendingRegs = state.otherApprovals.filter(
    (o) => o.entity_type === "REGULARIZATION" && o.status === "PENDING"
  ).length;
  const pendingQuotes = state.otherApprovals.filter(
    (o) => o.entity_type === "QUOTATION" && (o.status === "PENDING" || o.status === "PENDING_APPROVAL")
  ).length;

  return {
    pending_total: pendingLeaves + pendingRegs + pendingQuotes,
    pending_leaves: pendingLeaves,
    pending_regularizations: pendingRegs,
    pending_quotations: pendingQuotes,
    approved_this_month: approvedLeaves + 4,
    rejected_this_month: rejectedLeaves,
  };
}

export const approvalsApi = {
  getInbox: async (category?: string): Promise<UnifiedApprovalItem[]> => {
    const q = category ? `?category=${category}` : "";
    try {
      const res = await apiClient<UnifiedApprovalItem[]>(`/workflows/inbox${q}`);
      if (isServerlessDemoMode()) {
        return buildDemoInboxItems(category);
      }
      return res;
    } catch {
      return buildDemoInboxItems(category);
    }
  },

  getStats: async (): Promise<WorkflowStats> => {
    try {
      const res = await apiClient<WorkflowStats>("/workflows/stats");
      if (isServerlessDemoMode()) {
        return buildDemoStats();
      }
      return res;
    } catch {
      return buildDemoStats();
    }
  },

  processAction: async (
    entityType: string,
    entityId: string,
    action: "APPROVE" | "REJECT" | "RETURN",
    comments?: string,
    reviewerName: string = "Eleanor Vance (Manager)"
  ): Promise<{ success: boolean; new_status: string }> => {
    const upperType = entityType.toUpperCase();
    try {
      const res = await apiClient<{ success: boolean; new_status: string }>(
        `/workflows/${entityType.toLowerCase()}/${entityId}/action`,
        {
          method: "POST",
          body: JSON.stringify({ action, comments }),
        }
      );
      if (upperType === "LEAVE") {
        demoStore.reviewLeave({ requestId: entityId, action, reviewerName, remarks: comments });
      } else {
        demoStore.reviewOtherApproval(entityId, action);
      }
      return res;
    } catch {
      if (upperType === "LEAVE") {
        const updated = demoStore.reviewLeave({
          requestId: entityId,
          action,
          reviewerName,
          remarks: comments,
        });
        return {
          success: true,
          new_status: updated?.status || (action === "APPROVE" ? "APPROVED" : "REJECTED"),
        };
      }
      demoStore.reviewOtherApproval(entityId, action);
      return {
        success: true,
        new_status: action === "APPROVE" ? "APPROVED" : action === "REJECT" ? "REJECTED" : "RETURNED",
      };
    }
  },
};
