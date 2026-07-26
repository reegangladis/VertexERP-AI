import { apiClient } from './apiClient';

export interface MLDeployment {
  id: string;
  organization_id: string;
  model_id: string;
  model_version_id: string;
  name: string;
  environment: string;
  status: string;
  strategy: string;
  target_traffic_percentage: number;
  active_version: string;
  endpoint_url?: string;
  config_json?: Record<string, any>;
  created_at: string;
  updated_at: string;
  history?: DeploymentHistory[];
}

export interface DeploymentHistory {
  id: string;
  deployment_id: string;
  previous_version_id?: string;
  new_version_id: string;
  action: string;
  status: string;
  triggered_by: string;
  notes?: string;
  created_at: string;
}

export interface PipelineTemplate {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  pipeline_type: string;
  version: string;
  definition_json?: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PipelineRun {
  id: string;
  organization_id: string;
  template_id: string;
  model_id?: string;
  model_version_id?: string;
  run_name: string;
  status: string;
  metrics_json?: Record<string, any>;
  logs?: string;
  created_at: string;
  completed_at?: string;
}

export interface ModelApproval {
  id: string;
  organization_id: string;
  model_version_id: string;
  request_date: string;
  requested_by: string;
  target_environment: string;
  approval_status: string;
  approver?: string;
  decision_date?: string;
  compliance_metadata_json?: Record<string, any>;
  comments?: string;
  created_at: string;
}

export interface ModelMonitoringMetric {
  id: string;
  organization_id: string;
  deployment_id: string;
  metric_name: string;
  metric_value: number;
  timestamp: string;
}

export interface DriftReport {
  id: string;
  organization_id: string;
  deployment_id: string;
  drift_type: string;
  feature_name?: string;
  drift_score: number;
  status: string;
  metrics_json?: Record<string, any>;
  created_at: string;
}

export interface RetrainingJob {
  id: string;
  organization_id: string;
  model_id: string;
  trigger_type: string;
  status: string;
  config_json?: Record<string, any>;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

export const mlopsService = {
  // Deployments
  async getDeployments(): Promise<MLDeployment[]> {
    const res = await apiClient.get('/api/v1/mlops/deployments');
    return res.data;
  },

  async getDeployment(id: string): Promise<MLDeployment> {
    const res = await apiClient.get(`/api/v1/mlops/deployments/${id}`);
    return res.data;
  },

  async createDeployment(data: Partial<MLDeployment>): Promise<MLDeployment> {
    const res = await apiClient.post('/api/v1/mlops/deployments', data);
    return res.data;
  },

  async updateTraffic(id: string, targetTrafficPercentage: number): Promise<MLDeployment> {
    const res = await apiClient.put(`/api/v1/mlops/deployments/${id}/traffic`, {
      target_traffic_percentage: targetTrafficPercentage,
    });
    return res.data;
  },

  async rollbackDeployment(id: string, targetVersionId: string, username: string, notes?: string): Promise<MLDeployment> {
    const res = await apiClient.post(`/api/v1/mlops/deployments/${id}/rollback`, {
      target_version_id: targetVersionId,
      triggered_by: username,
      notes,
    });
    return res.data;
  },

  // Pipeline Templates
  async createPipelineTemplate(data: any): Promise<PipelineTemplate> {
    const res = await apiClient.post('/api/v1/mlops/pipelines/templates', data);
    return res.data;
  },

  async getPipelineTemplates(): Promise<PipelineTemplate[]> {
    const res = await apiClient.get('/api/v1/mlops/pipelines/templates');
    return res.data;
  },

  // Pipeline Runs
  async triggerPipelineRun(data: { template_id: string; run_name: string; model_id?: string; model_version_id?: string }): Promise<PipelineRun> {
    const res = await apiClient.post('/api/v1/mlops/pipelines/runs', data);
    return res.data;
  },

  async getPipelineRuns(): Promise<PipelineRun[]> {
    const res = await apiClient.get('/api/v1/mlops/pipelines/runs');
    return res.data;
  },

  async getPipelineRun(id: string): Promise<PipelineRun> {
    const res = await apiClient.get(`/api/v1/mlops/pipelines/runs/${id}`);
    return res.data;
  },

  // Model Governance & Approvals
  async requestPromotionApproval(data: { model_version_id: string; requested_by: string; target_environment: string; comments?: string }): Promise<ModelApproval> {
    const res = await apiClient.post('/api/v1/mlops/approvals', data);
    return res.data;
  },

  async getApprovals(status?: string): Promise<ModelApproval[]> {
    const url = status ? `/api/v1/mlops/approvals?status=${status}` : '/api/v1/mlops/approvals';
    const res = await apiClient.get(url);
    return res.data;
  },

  async decideApproval(id: string, data: { approval_status: string; approver: string; comments?: string }): Promise<ModelApproval> {
    const res = await apiClient.post(`/api/v1/mlops/approvals/${id}/decide`, data);
    return res.data;
  },

  // Model Monitoring
  async ingestTelemetryMetric(deploymentId: string, data: { metric_name: string; metric_value: number }): Promise<ModelMonitoringMetric> {
    const res = await apiClient.post(`/api/v1/mlops/monitoring/${deploymentId}/metrics`, data);
    return res.data;
  },

  async getTelemetryMetrics(deploymentId: string, limit?: number): Promise<ModelMonitoringMetric[]> {
    const url = limit ? `/api/v1/mlops/monitoring/${deploymentId}/metrics?limit=${limit}` : `/api/v1/mlops/monitoring/${deploymentId}/metrics`;
    const res = await apiClient.get(url);
    return res.data;
  },

  async evaluateDrift(deploymentId: string, data: { drift_type: string; feature_name?: string; drift_score: number; metrics_json?: any }): Promise<DriftReport> {
    const res = await apiClient.post(`/api/v1/mlops/monitoring/${deploymentId}/drift`, data);
    return res.data;
  },

  async getDriftReports(deploymentId: string): Promise<DriftReport[]> {
    const res = await apiClient.get(`/api/v1/mlops/monitoring/${deploymentId}/drift`);
    return res.data;
  },

  // Retraining
  async triggerRetraining(data: { model_id: string; trigger_type: string; config_json?: any }): Promise<RetrainingJob> {
    const res = await apiClient.post('/api/v1/mlops/retraining', data);
    return res.data;
  },

  async getRetrainingHistory(modelId?: string): Promise<RetrainingJob[]> {
    const url = modelId ? `/api/v1/mlops/retraining?model_id=${modelId}` : '/api/v1/mlops/retraining';
    const res = await apiClient.get(url);
    return res.data;
  },
};
