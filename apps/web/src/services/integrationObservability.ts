import { apiClient } from './apiClient';

export interface APIKey {
  id: string;
  organization_id: string;
  client_name: string;
  api_key: string;
  secret_key: string;
  permissions: string;
  expires_at?: string;
  status: string;
  created_at: string;
}

export interface Webhook {
  id: string;
  organization_id: string;
  event_name: string;
  endpoint: string;
  secret: string;
  status: string;
  created_at: string;
}

export interface Notification {
  id: string;
  organization_id: string;
  user_id?: string;
  notification_type: string;
  title: string;
  message: string;
  channel: string;
  status: string;
  sent_at: string;
  created_at: string;
}

export interface DeploymentHistory {
  id: string;
  environment: string;
  version: string;
  commit_hash: string;
  deployed_by: string;
  started_at: string;
  completed_at?: string;
  status: string;
  created_at: string;
}

export interface BackupJob {
  id: string;
  backup_name: string;
  storage_provider: string;
  backup_size: number;
  started_at: string;
  completed_at?: string;
  status: string;
  created_at: string;
}

export interface OpsDashboardSummary {
  active_api_keys: number;
  active_webhooks: number;
  notifications_sent: number;
  overall_system_status: string;
  avg_cpu_usage_pct: number;
  avg_memory_usage_pct: number;
  avg_latency_ms: number;
  total_deployments: number;
  total_backups_completed: number;
  active_system_alerts: number;
}

export const integrationObservabilityService = {
  // Dashboard
  getDashboardSummary: async (orgId: string): Promise<OpsDashboardSummary> => {
    const res = await apiClient.get('/api/v1/ops/dashboard', { params: { org_id: orgId } });
    return res.data;
  },

  // API Keys
  getAPIKeys: async (orgId: string): Promise<APIKey[]> => {
    const res = await apiClient.get('/api/v1/ops/api-keys', { params: { org_id: orgId } });
    return res.data;
  },

  generateAPIKey: async (data: Partial<APIKey>): Promise<APIKey> => {
    const res = await apiClient.post('/api/v1/ops/api-keys', data);
    return res.data;
  },

  // Webhooks
  getWebhooks: async (orgId: string): Promise<Webhook[]> => {
    const res = await apiClient.get('/api/v1/ops/webhooks', { params: { org_id: orgId } });
    return res.data;
  },

  registerWebhook: async (data: Partial<Webhook>): Promise<Webhook> => {
    const res = await apiClient.post('/api/v1/ops/webhooks', data);
    return res.data;
  },

  // Notifications
  getNotifications: async (orgId: string): Promise<Notification[]> => {
    const res = await apiClient.get('/api/v1/ops/notifications', { params: { org_id: orgId } });
    return res.data;
  },

  sendNotification: async (data: Partial<Notification>): Promise<Notification> => {
    const res = await apiClient.post('/api/v1/ops/notifications', data);
    return res.data;
  },

  // Deployments
  getDeployments: async (): Promise<DeploymentHistory[]> => {
    const res = await apiClient.get('/api/v1/ops/deployments');
    return res.data;
  },

  triggerDeployment: async (data: Partial<DeploymentHistory>): Promise<DeploymentHistory> => {
    const res = await apiClient.post('/api/v1/ops/deployments', data);
    return res.data;
  },

  // Backups
  getBackups: async (): Promise<BackupJob[]> => {
    const res = await apiClient.get('/api/v1/ops/backups');
    return res.data;
  },

  createBackup: async (data: Partial<BackupJob>): Promise<BackupJob> => {
    const res = await apiClient.post('/api/v1/ops/backups', data);
    return res.data;
  },
};
