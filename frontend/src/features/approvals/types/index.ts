export interface UnifiedApprovalItem {
  id: string;
  entity_type: "LEAVE" | "REGULARIZATION" | "QUOTATION" | "EXPENSE";
  entity_id: string;
  requester_name: string;
  requester_email?: string;
  title: string;
  summary: string;
  amount?: number;
  currency?: string;
  status: string;
  priority: "LOW" | "MEDIUM" | "HIGH";
  created_at?: string;
  details?: Record<string, any>;
}

export interface WorkflowStats {
  pending_total: number;
  pending_leaves: number;
  pending_regularizations: number;
  pending_quotations: number;
  approved_this_month: number;
  rejected_this_month: number;
}
