import { apiClient } from './apiClient';

export interface CopilotSession {
  id: string;
  organization_id: string;
  user_id: string;
  title: string;
  is_pinned: boolean;
  current_state?: any;
  created_at: string;
  updated_at: string;
}

export interface CopilotMessage {
  id: string;
  session_id: string;
  role: string;
  content: string;
  prompt_tokens: number;
  completion_tokens: number;
  latency_ms: number;
  tool_calls?: any[];
  citations?: any[];
  generated_from?: string;
  feedback_rating?: number;
  created_at: string;
}

export interface ChatResponse {
  session_id: string;
  user_message: CopilotMessage;
  assistant_message: CopilotMessage;
}

export interface CopilotPrompt {
  id: string;
  organization_id?: string;
  name: string;
  type: string;
  department?: string;
  template: string;
  variables: string[];
  version: string;
  is_active: boolean;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface ToolRegistry {
  id: string;
  name: string;
  description: string;
  parameters_schema: any;
  is_active: boolean;
  required_role?: string;
  created_at: string;
  updated_at: string;
}

export interface ToolExecution {
  id: string;
  message_id?: string;
  session_id: string;
  tool_name: string;
  input_arguments: any;
  output_result?: any;
  status: string;
  execution_time_ms: number;
  error_message?: string;
  created_at: string;
}

export interface ConversationFeedback {
  id: string;
  message_id: string;
  user_id: string;
  organization_id: string;
  rating: number;
  comments?: string;
  created_at: string;
}

export interface CopilotAnalytics {
  total_prompt_tokens: number;
  total_completion_tokens: number;
  average_latency_ms: number;
  tool_success_rate: number;
  total_tool_executions: number;
  average_feedback_rating: number;
  total_feedbacks: number;
}

export const copilotService = {
  // Session APIs
  createSession: async (title?: string): Promise<CopilotSession> => {
    const res = await apiClient.post('/api/v1/copilot/sessions', { title });
    return res.data.data || res.data;
  },

  listSessions: async (): Promise<CopilotSession[]> => {
    const res = await apiClient.get('/api/v1/copilot/sessions');
    return res.data.data || res.data;
  },

  getSession: async (sessionId: string): Promise<CopilotSession> => {
    const res = await apiClient.get(`/api/v1/copilot/sessions/${sessionId}`);
    return res.data.data || res.data;
  },

  updateSession: async (sessionId: string, data: Partial<CopilotSession>): Promise<CopilotSession> => {
    const res = await apiClient.put(`/api/v1/copilot/sessions/${sessionId}`, data);
    return res.data.data || res.data;
  },

  deleteSession: async (sessionId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/copilot/sessions/${sessionId}`);
  },

  // Chat APIs
  sendChatMessage: async (
    sessionId: string,
    content: string,
    provider: string = 'openai',
    modelName?: string,
    temperature: number = 0.7,
    department?: string
  ): Promise<ChatResponse> => {
    const res = await apiClient.post(`/api/v1/copilot/sessions/${sessionId}/chat`, {
      content,
      provider,
      model_name: modelName,
      temperature,
      department,
    });
    return res.data.data || res.data;
  },

  listMessages: async (sessionId: string): Promise<CopilotMessage[]> => {
    const res = await apiClient.get(`/api/v1/copilot/sessions/${sessionId}/messages`);
    return res.data.data || res.data;
  },

  // Prompt APIs
  listPrompts: async (): Promise<CopilotPrompt[]> => {
    const res = await apiClient.get('/api/v1/copilot/prompts');
    return res.data.data || res.data;
  },

  createPrompt: async (prompt: Partial<CopilotPrompt>): Promise<CopilotPrompt> => {
    const res = await apiClient.post('/api/v1/copilot/prompts', prompt);
    return res.data.data || res.data;
  },

  updatePrompt: async (promptId: string, prompt: Partial<CopilotPrompt>): Promise<CopilotPrompt> => {
    const res = await apiClient.put(`/api/v1/copilot/prompts/${promptId}`, prompt);
    return res.data.data || res.data;
  },

  deletePrompt: async (promptId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/copilot/prompts/${promptId}`);
  },

  testPrompt: async (template: string, variables: any): Promise<string> => {
    const res = await apiClient.post('/api/v1/copilot/prompts/test', { template, variables });
    return res.data.data?.rendered || res.data.rendered || '';
  },

  // Tool APIs
  listTools: async (): Promise<ToolRegistry[]> => {
    const res = await apiClient.get('/api/v1/copilot/tools');
    return res.data.data || res.data;
  },

  updateToolStatus: async (toolName: string, isActive: boolean): Promise<ToolRegistry> => {
    const res = await apiClient.put(`/api/v1/copilot/tools/${toolName}/status`, null, {
      params: { is_active: isActive },
    });
    return res.data.data || res.data;
  },

  getToolExecutions: async (sessionId: string): Promise<ToolExecution[]> => {
    const res = await apiClient.get(`/api/v1/copilot/sessions/${sessionId}/tool-executions`);
    return res.data.data || res.data;
  },

  // Feedback APIs
  submitFeedback: async (messageId: string, rating: number, comments?: string): Promise<ConversationFeedback> => {
    const res = await apiClient.post(`/api/v1/copilot/messages/${messageId}/feedback`, {
      rating,
      comments,
    });
    return res.data.data || res.data;
  },

  // Analytics APIs
  getAnalytics: async (): Promise<CopilotAnalytics> => {
    const res = await apiClient.get('/api/v1/copilot/analytics');
    return res.data.data || res.data;
  },
};
