/**
 * AI Platform & Copilot Domain Type Definitions
 * VertexERP AI V2
 */

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface PendingActionProposal {
  action_id: string;
  action_type: string;
  tool_name: string;
  parameters: Record<string, any>;
  preview_summary: string;
  expires_at: string;
  confirmation_token: string;
  requires_confirmation: boolean;
}

export interface ToolCall {
  id: string;
  type: string;
  function: {
    name: string;
    arguments: string;
  };
}

export interface ToolExecutionRecord {
  success: boolean;
  tool_name: string;
  result?: any;
  error?: string;
  execution_time_ms?: number;
}

export interface CopilotChatRequest {
  conversation_id?: string;
  message: string;
  context?: Record<string, any>;
  stream?: boolean;
  tools_enabled?: boolean;
  provider?: string;
  model?: string;
}

export interface CopilotChatResponse {
  conversation_id: string;
  message_id: string;
  role: string;
  content: string;
  tool_calls?: ToolCall[];
  tool_executions?: ToolExecutionRecord[];
  pending_action?: PendingActionProposal;
  usage: TokenUsage;
  cost_usd: number;
  latency_ms?: number;
}

export interface ConfirmActionRequest {
  action_id: string;
  confirmation_token: string;
  confirmed: boolean;
  user_notes?: string;
}

export interface ConfirmActionResponse {
  action_id: string;
  status: "executed" | "rejected" | "expired" | "failed";
  tool_name: string;
  result?: Record<string, any>;
  error?: string;
  executed_at?: string;
}

export interface AIConversation {
  id: string;
  tenant_id: string;
  organization_id?: string;
  user_id: string;
  title: string;
  domain_context?: string;
  context_type?: string;
  context_id?: string;
  model_used?: string;
  total_prompt_tokens?: number;
  total_completion_tokens?: number;
  total_tokens?: number;
  total_cost?: number;
  estimated_cost_usd?: number;
  message_count?: number;
  is_pinned?: boolean;
  is_active?: boolean;
  is_archived?: boolean;
  created_at: string;
  updated_at: string;
  metadata_json?: Record<string, any>;
}

export interface AIMessage {
  id: string;
  conversation_id: string;
  tenant_id?: string;
  role: "system" | "user" | "assistant" | "tool";
  content?: string;
  tool_calls?: any[];
  tool_call_id?: string;
  token_count?: number;
  prompt_tokens?: number;
  completion_tokens?: number;
  total_tokens?: number;
  cost?: number;
  cost_usd?: number;
  latency_ms?: number;
  is_error?: boolean;
  created_at: string;
}

export interface AIUsageSummaryItem {
  provider: string;
  model: string;
  total_calls: number;
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_tokens: number;
  total_cost_usd: number;
  avg_latency_ms: number;
  error_rate: number;
}

export interface AIUsageSummary {
  total_calls: number;
  total_tokens: number;
  total_cost_usd: number;
  by_provider: AIUsageSummaryItem[];
  by_feature: Record<string, any>;
  date_from?: string;
  date_to?: string;
}

export interface ERPToolInfo {
  name: string;
  description: string;
  action_type: string;
  is_mutation: boolean;
  parameters_schema: Record<string, any>;
}

export interface RAGDocument {
  id: string;
  tenant_id: string;
  organization_id: string;
  title: string;
  description?: string;
  file_type: string;
  file_size_bytes: number;
  access_level: "PUBLIC" | "INTERNAL" | "CONFIDENTIAL" | "RESTRICTED";
  allowed_departments: string[];
  allowed_roles: string[];
  tags: string[];
  metadata_json: Record<string, any>;
  is_active: boolean;
  active_version?: number;
  total_chunks?: number;
  latest_job_status?: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED" | "NONE";
  created_at: string;
  updated_at: string;
}

export interface RAGDocumentVersion {
  id: string;
  document_id: string;
  version_number: number;
  changelog?: string;
  checksum: string;
  is_active: boolean;
  created_at: string;
}

export interface RAGDocumentChunk {
  id: string;
  document_id: string;
  version_id: string;
  chunk_index: number;
  content: string;
  token_count: number;
  char_count: number;
  section_heading?: string;
  metadata_json: Record<string, any>;
  created_at: string;
}

export interface RAGDocumentDetail extends RAGDocument {
  versions: RAGDocumentVersion[];
  recent_chunks: RAGDocumentChunk[];
}

export interface RAGIngestionJob {
  id: string;
  tenant_id: string;
  organization_id: string;
  document_id: string;
  version_id: string;
  status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
  retry_count: number;
  max_retries: number;
  error_message?: string;
  dead_letter: boolean;
  dead_letter_reason?: string;
  metrics_json: Record<string, any>;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface RAGSearchResultItem {
  chunk_id: string;
  document_id: string;
  document_title: string;
  version_number: number;
  chunk_index: number;
  content: string;
  section_heading?: string;
  vector_score: number;
  lexical_score: number;
  composite_score: number;
  metadata: Record<string, any>;
}

export interface RAGSearchResponse {
  query: string;
  total_results: number;
  results: RAGSearchResultItem[];
  latency_ms: number;
}

export interface RAGQueryCitation {
  document_id: string;
  document_title: string;
  version_number: number;
  chunk_index: number;
  section_heading?: string;
  snippet: string;
  relevance_score: number;
}

export interface RAGQueryResponse {
  query: string;
  answer: string;
  citations: RAGQueryCitation[];
  retrieved_chunks_count: number;
  provider_used: string;
  model_used: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  cost_usd: number;
  latency_ms: number;
}

