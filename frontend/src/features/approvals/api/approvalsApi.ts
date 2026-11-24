import { apiClient } from "@/lib/api-client";
import { UnifiedApprovalItem, WorkflowStats } from "../types";

export const approvalsApi = {
  getInbox: (category?: string) => {
    const q = category ? `?category=${category}` : "";
    return apiClient<UnifiedApprovalItem[]>(`/workflows/inbox${q}`);
  },

  getStats: () => apiClient<WorkflowStats>("/workflows/stats"),

  processAction: (
    entityType: string,
    entityId: string,
    action: "APPROVE" | "REJECT" | "RETURN",
    comments?: string
  ) =>
    apiClient<{ success: boolean; new_status: string }>(
      `/workflows/${entityType.toLowerCase()}/${entityId}/action`,
      {
        method: "POST",
        body: JSON.stringify({ action, comments }),
      }
    ),
};
