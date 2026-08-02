import { apiClient } from './apiClient';

export interface KnowledgeCollection {
  id: string;
  organization_id: string;
  name: string;
  slug: string;
  description?: string;
  category: string;
  tags: string[];
  is_public: boolean;
  metadata_json?: any;
  created_at: string;
  updated_at: string;
}

export interface RAGDocument {
  id: string;
  organization_id: string;
  collection_id?: string;
  title: string;
  file_name: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  document_type: string;
  format: string;
  current_version: number;
  status: string;
  approval_status: string;
  retention_days?: number;
  metadata_json?: any;
  created_at: string;
  updated_at: string;
}

export interface CitationSource {
  document_id: string;
  document_title: string;
  chunk_id: string;
  chunk_index: number;
  snippet: string;
  score: number;
}

export interface RetrievalChunkResult {
  chunk_id: string;
  document_id: string;
  document_title: string;
  document_type: string;
  category: string;
  content: string;
  score: number;
  chunk_index: number;
  metadata?: any;
}

export interface RetrievalResponse {
  query: string;
  results: RetrievalChunkResult[];
  total_found: number;
  execution_time_ms: number;
  search_type: string;
}

export interface RAGChatSession {
  id: string;
  organization_id: string;
  user_id: string;
  title: string;
  is_pinned: boolean;
  context_metadata?: any;
  created_at: string;
  updated_at: string;
}

export interface RAGChatMessage {
  id: string;
  session_id: string;
  role: string;
  content: string;
  prompt_tokens: number;
  completion_tokens: number;
  citations?: CitationSource[];
  feedback_rating?: number;
  feedback_text?: string;
  created_at: string;
}

export interface ChatPromptResponse {
  session_id: string;
  user_message: RAGChatMessage;
  assistant_message: RAGChatMessage;
}

export const ragService = {
  // Collections
  listCollections: async (category?: string): Promise<KnowledgeCollection[]> => {
    const params = category ? { category } : {};
    const res = await apiClient.get<KnowledgeCollection[]>('/api/v1/rag/collections', { params });
    return res.data;
  },

  createCollection: async (data: Partial<KnowledgeCollection>): Promise<KnowledgeCollection> => {
    const res = await apiClient.post<KnowledgeCollection>('/api/v1/rag/collections', data);
    return res.data;
  },

  deleteCollection: async (collectionId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/rag/collections/${collectionId}`);
  },

  // Documents
  listDocuments: async (filters?: {
    collection_id?: string;
    category?: string;
    document_type?: string;
    status?: string;
    search?: string;
  }): Promise<RAGDocument[]> => {
    const res = await apiClient.get<RAGDocument[]>('/api/v1/rag/documents', { params: filters });
    return res.data;
  },

  uploadDocument: async (formData: FormData): Promise<RAGDocument> => {
    const res = await apiClient.post<RAGDocument>('/api/v1/rag/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  deleteDocument: async (docId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/rag/documents/${docId}`);
  },

  // Search
  search: async (params: {
    query: string;
    collection_ids?: string[];
    categories?: string[];
    document_types?: string[];
    tags?: string[];
    top_k?: number;
    search_type?: string;
    provider?: string;
    min_score?: number;
  }): Promise<RetrievalResponse> => {
    const res = await apiClient.post<RetrievalResponse>('/api/v1/rag/retrieval/search', params);
    return res.data;
  },

  // Chat
  listSessions: async (): Promise<RAGChatSession[]> => {
    const res = await apiClient.get<RAGChatSession[]>('/api/v1/rag/chat/sessions');
    return res.data;
  },

  createSession: async (title?: string): Promise<RAGChatSession> => {
    const res = await apiClient.post<RAGChatSession>('/api/v1/rag/chat/sessions', null, {
      params: { title },
    });
    return res.data;
  },

  getSessionMessages: async (sessionId: string): Promise<RAGChatMessage[]> => {
    const res = await apiClient.get<RAGChatMessage[]>(`/api/v1/rag/chat/sessions/${sessionId}/messages`);
    return res.data;
  },

  sendMessage: async (
    sessionId: string,
    params: {
      query: string;
      collection_ids?: string[];
      provider?: string;
      model_name?: string;
      temperature?: number;
      top_k?: number;
      search_type?: string;
    }
  ): Promise<ChatPromptResponse> => {
    const res = await apiClient.post<ChatPromptResponse>(
      `/api/v1/rag/chat/sessions/${sessionId}/messages`,
      params
    );
    return res.data;
  },

  togglePinSession: async (sessionId: string): Promise<RAGChatSession> => {
    const res = await apiClient.post<RAGChatSession>(`/api/v1/rag/chat/sessions/${sessionId}/pin`);
    return res.data;
  },

  // Feedback
  submitFeedback: async (feedback: {
    chat_message_id?: string;
    chunk_id?: string;
    rating: number;
    feedback_type: string;
    comments?: string;
  }): Promise<any> => {
    const res = await apiClient.post('/api/v1/rag/chat/feedback', feedback);
    return res.data;
  },
};
