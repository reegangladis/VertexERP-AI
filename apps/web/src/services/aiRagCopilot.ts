import { apiClient } from './apiClient';

export interface KnowledgeCollection {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  visibility: string;
  status: string;
  created_at: string;
}

export interface RAGDocument {
  id: string;
  collection_id: string;
  document_name: string;
  file_type: string;
  file_size: number;
  status: string;
  created_at: string;
}

export interface RAGChatMessage {
  id: string;
  session_id: string;
  role: string;
  message: string;
  tokens: number;
  latency: number;
  created_at: string;
}

export interface RAGChatSession {
  id: string;
  organization_id: string;
  session_name: string;
  model_name: string;
  temperature: number;
  status: string;
  created_at: string;
  messages: RAGChatMessage[];
}

export interface PromptTemplate {
  id: string;
  name: string;
  category: string;
  description?: string;
  system_prompt: string;
  status: string;
  created_at: string;
}

export interface AIAgent {
  id: string;
  organization_id: string;
  agent_name: string;
  agent_type: string;
  system_prompt: string;
  model: string;
  temperature: number;
  status: string;
  created_at: string;
}

export interface ToolRegistry {
  id: string;
  tool_name: string;
  tool_description: string;
  tool_type: string;
  endpoint?: string;
  enabled: boolean;
  created_at: string;
}

export interface AIDashboardSummary {
  total_documents: number;
  total_embeddings: number;
  total_collections: number;
  active_chat_sessions: number;
  total_agent_runs: number;
  average_response_time_sec: number;
  total_prompt_templates: number;
  total_token_usage: number;
}

export const aiRagCopilotService = {
  // Dashboard
  getDashboardSummary: async (orgId: string): Promise<AIDashboardSummary> => {
    const res = await apiClient.get('/api/v1/ai/dashboard', { params: { org_id: orgId } });
    return res.data;
  },

  // Collections
  getCollections: async (orgId: string): Promise<KnowledgeCollection[]> => {
    const res = await apiClient.get('/api/v1/ai/collections', { params: { org_id: orgId } });
    return res.data;
  },

  createCollection: async (data: Partial<KnowledgeCollection>): Promise<KnowledgeCollection> => {
    const res = await apiClient.post('/api/v1/ai/collections', data);
    return res.data;
  },

  // Documents
  getDocuments: async (collectionId?: string): Promise<RAGDocument[]> => {
    const res = await apiClient.get('/api/v1/ai/documents', { params: { collection_id: collectionId } });
    return res.data;
  },

  ingestDocument: async (data: any): Promise<RAGDocument> => {
    const res = await apiClient.post('/api/v1/ai/documents', data);
    return res.data;
  },

  // Copilot Chat
  getChatSessions: async (orgId: string): Promise<RAGChatSession[]> => {
    const res = await apiClient.get('/api/v1/ai/copilot/sessions', { params: { org_id: orgId } });
    return res.data;
  },

  createChatSession: async (data: any): Promise<RAGChatSession> => {
    const res = await apiClient.post('/api/v1/ai/copilot/sessions', data);
    return res.data;
  },

  sendMessage: async (sessionId: string, message: string): Promise<RAGChatMessage> => {
    const res = await apiClient.post('/api/v1/ai/copilot/chat', {
      session_id: sessionId,
      role: 'user',
      message: message,
    });
    return res.data;
  },

  // Prompts
  getPromptTemplates: async (): Promise<PromptTemplate[]> => {
    const res = await apiClient.get('/api/v1/ai/prompts');
    return res.data;
  },

  createPromptTemplate: async (data: any): Promise<PromptTemplate> => {
    const res = await apiClient.post('/api/v1/ai/prompts', data);
    return res.data;
  },

  // Agents
  getAgents: async (orgId: string): Promise<AIAgent[]> => {
    const res = await apiClient.get('/api/v1/ai/agents', { params: { org_id: orgId } });
    return res.data;
  },

  createAgent: async (data: any): Promise<AIAgent> => {
    const res = await apiClient.post('/api/v1/ai/agents', data);
    return res.data;
  },

  runAgent: async (agentId: string, inputText: string): Promise<any> => {
    const res = await apiClient.post('/api/v1/ai/agents/run', {
      agent_id: agentId,
      input_text: inputText,
    });
    return res.data;
  },

  // Tools
  getTools: async (): Promise<ToolRegistry[]> => {
    const res = await apiClient.get('/api/v1/ai/tools');
    return res.data;
  },
};
