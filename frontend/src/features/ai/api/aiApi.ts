/**
 * AI Platform & Copilot API Client
 * VertexERP AI V2
 */

import { apiClient } from "@/lib/api-client";
import {
  AIConversation,
  AIMessage,
  AIUsageSummary,
  ConfirmActionRequest,
  ConfirmActionResponse,
  CopilotChatRequest,
  CopilotChatResponse,
  ERPToolInfo,
} from "../types";

export const aiApi = {
  /**
   * Send a chat message to Vertex Copilot with optional tool execution.
   */
  async sendChatMessage(payload: CopilotChatRequest): Promise<CopilotChatResponse> {
    return apiClient<CopilotChatResponse>("/ai/copilot/chat", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * Confirm or reject a pending human-in-the-loop AI mutation proposal.
   */
  async confirmAction(payload: ConfirmActionRequest): Promise<ConfirmActionResponse> {
    return apiClient<ConfirmActionResponse>("/ai/copilot/confirm-action", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * List active conversations for the current user.
   */
  async listConversations(skip = 0, limit = 50): Promise<{ items: AIConversation[]; total: number }> {
    return apiClient<{ items: AIConversation[]; total: number }>(
      `/ai/copilot/conversations?skip=${skip}&limit=${limit}`
    );
  },

  /**
   * Create a new conversation.
   */
  async createConversation(title?: string): Promise<AIConversation> {
    return apiClient<AIConversation>("/ai/copilot/conversations", {
      method: "POST",
      body: JSON.stringify({ title: title || "New Conversation" }),
    });
  },

  /**
   * Get single conversation by ID.
   */
  async getConversation(conversationId: string): Promise<AIConversation> {
    return apiClient<AIConversation>(`/ai/copilot/conversations/${conversationId}`);
  },

  /**
   * Update conversation title or pinned status.
   */
  async updateConversation(
    conversationId: string,
    data: { title?: string; is_pinned?: boolean; is_archived?: boolean }
  ): Promise<AIConversation> {
    return apiClient<AIConversation>(`/ai/copilot/conversations/${conversationId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  /**
   * Archive / soft-delete conversation.
   */
  async deleteConversation(conversationId: string): Promise<void> {
    return apiClient<void>(`/ai/copilot/conversations/${conversationId}`, {
      method: "DELETE",
    });
  },

  /**
   * Get chronological message history for a conversation.
   */
  async getConversationMessages(
    conversationId: string,
    skip = 0,
    limit = 100
  ): Promise<{ items: AIMessage[]; total: number }> {
    return apiClient<{ items: AIMessage[]; total: number }>(
      `/ai/copilot/conversations/${conversationId}/messages?skip=${skip}&limit=${limit}`
    );
  },

  /**
   * Get aggregated AI usage telemetry and token cost metrics.
   */
  async getUsageSummary(dateFrom?: string, dateTo?: string): Promise<AIUsageSummary> {
    const params = new URLSearchParams();
    if (dateFrom) params.append("date_from", dateFrom);
    if (dateTo) params.append("date_to", dateTo);
    const query = params.toString() ? `?${params.toString()}` : "";
    return apiClient<AIUsageSummary>(`/ai/usage/summary${query}`);
  },

  /**
   * List available ERP domain tools and their parameters schemas.
   */
  async getAvailableTools(): Promise<{ count: number; tools: ERPToolInfo[] }> {
    return apiClient<{ count: number; tools: ERPToolInfo[] }>("/ai/usage/tools");
  },

  // ---------------------------------------------------------------------------
  // RAG & Knowledge Base Endpoints
  // ---------------------------------------------------------------------------
  /**
   * List knowledge base documents with search, access level, and tag filters.
   */
  async listDocuments(params?: {
    access_level?: string;
    tag?: string;
    search?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ items: any[]; total: number; skip: number; limit: number }> {
    const q = new URLSearchParams();
    if (params?.access_level) q.append("access_level", params.access_level);
    if (params?.tag) q.append("tag", params.tag);
    if (params?.search) q.append("search", params.search);
    if (params?.skip !== undefined) q.append("skip", String(params.skip));
    if (params?.limit !== undefined) q.append("limit", String(params.limit));
    const qs = q.toString() ? `?${q.toString()}` : "";
    return apiClient<{ items: any[]; total: number; skip: number; limit: number }>(`/ai/rag/documents${qs}`);
  },

  /**
   * Get detailed document with versions and chunks.
   */
  async getDocumentDetails(documentId: string): Promise<any> {
    return apiClient<any>(`/ai/rag/documents/${documentId}`);
  },

  /**
   * Upload / create a new knowledge document.
   */
  async createDocument(payload: {
    title: string;
    description?: string;
    raw_content: string;
    file_type?: string;
    access_level?: string;
    allowed_departments?: string[];
    allowed_roles?: string[];
    tags?: string[];
  }): Promise<{ message: string; document_id: string; job_id: string; job_status: string }> {
    return apiClient<{ message: string; document_id: string; job_id: string; job_status: string }>(
      "/ai/rag/documents",
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  },

  /**
   * Create a new document version.
   */
  async createDocumentVersion(
    documentId: string,
    payload: { raw_content: string; changelog?: string }
  ): Promise<{ message: string; version_id: string; version_number: number; job_id: string; job_status: string }> {
    return apiClient<{ message: string; version_id: string; version_number: number; job_id: string; job_status: string }>(
      `/ai/rag/documents/${documentId}/versions`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  },

  /**
   * Delete / deactivate document.
   */
  async deleteDocument(documentId: string): Promise<{ message: string }> {
    return apiClient<{ message: string }>(`/ai/rag/documents/${documentId}`, {
      method: "DELETE",
    });
  },

  /**
   * Get ingestion job status.
   */
  async getIngestionJob(jobId: string): Promise<any> {
    return apiClient<any>(`/ai/rag/jobs/${jobId}`);
  },

  /**
   * Retry failed or dead-letter ingestion job.
   */
  async retryIngestionJob(jobId: string): Promise<any> {
    return apiClient<any>(`/ai/rag/jobs/${jobId}/retry`, {
      method: "POST",
    });
  },

  /**
   * Vector & hybrid search against knowledge chunks.
   */
  async searchKnowledge(payload: {
    query: string;
    top_k?: number;
    min_score?: number;
  }): Promise<any> {
    return apiClient<any>("/ai/rag/search", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * End-to-end grounded RAG answering with verifiable structured citations.
   */
  async queryKnowledge(payload: {
    query: string;
    top_k?: number;
    provider?: string;
    model?: string;
  }): Promise<any> {
    return apiClient<any>("/ai/rag/query", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};
