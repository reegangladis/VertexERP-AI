import { apiClient } from './apiClient';

export interface Dataset {
  id: string;
  organization_id: string;
  dataset_name: string;
  dataset_type: string;
  source: string;
  schema_version: string;
  status: string;
  created_at: string;
}

export interface PipelineJob {
  id: string;
  organization_id: string;
  pipeline_name: string;
  schedule_cron?: string;
  status: string;
  created_at: string;
}

export interface ETLJob {
  id: string;
  job_name: string;
  source_type: string;
  target_type: string;
  status: string;
  created_at: string;
}

export interface FeatureStore {
  id: string;
  feature_name: string;
  feature_group: string;
  data_type: string;
  description?: string;
  version: string;
  status: string;
  created_at: string;
}

export interface MLModel {
  id: string;
  organization_id: string;
  model_name: string;
  algorithm: string;
  framework: string;
  problem_type: string;
  current_version: string;
  status: string;
  created_at: string;
}

export interface ModelVersion {
  id: string;
  model_id: string;
  version: string;
  metrics: string;
  artifact_path: string;
  registered_at: string;
}

export interface PredictionResult {
  prediction_id: string;
  model_version_id: string;
  prediction_output: any;
  latency_sec: number;
  confidence_score: number;
  status: string;
}

export interface DriftReport {
  id: string;
  model_id: string;
  drift_type: string;
  drift_score: number;
  threshold: number;
  status: string;
  generated_at: string;
}

export interface DataPlatformDashboardSummary {
  total_datasets: number;
  total_pipeline_runs: number;
  total_features_in_store: number;
  active_ml_models: number;
  total_predictions: number;
  active_drift_alerts: number;
  average_prediction_latency_ms: number;
  training_jobs_completed: number;
}

export const dataAnalyticsMlopsService = {
  // Dashboard
  getDashboardSummary: async (orgId: string): Promise<DataPlatformDashboardSummary> => {
    const res = await apiClient.get('/api/v1/analytics/dashboard', { params: { org_id: orgId } });
    return res.data;
  },

  // Datasets
  getDatasets: async (orgId: string): Promise<Dataset[]> => {
    const res = await apiClient.get('/api/v1/analytics/datasets', { params: { org_id: orgId } });
    return res.data;
  },

  createDataset: async (data: Partial<Dataset>): Promise<Dataset> => {
    const res = await apiClient.post('/api/v1/analytics/datasets', data);
    return res.data;
  },

  // Pipelines & ETL
  getPipelines: async (orgId: string): Promise<PipelineJob[]> => {
    const res = await apiClient.get('/api/v1/analytics/pipelines', { params: { org_id: orgId } });
    return res.data;
  },

  createPipeline: async (data: Partial<PipelineJob>): Promise<PipelineJob> => {
    const res = await apiClient.post('/api/v1/analytics/pipelines', data);
    return res.data;
  },

  getETLJobs: async (): Promise<ETLJob[]> => {
    const res = await apiClient.get('/api/v1/analytics/etl-jobs');
    return res.data;
  },

  createETLJob: async (data: Partial<ETLJob>): Promise<ETLJob> => {
    const res = await apiClient.post('/api/v1/analytics/etl-jobs', data);
    return res.data;
  },

  // Feature Store
  getFeatures: async (): Promise<FeatureStore[]> => {
    const res = await apiClient.get('/api/v1/analytics/features');
    return res.data;
  },

  createFeature: async (data: Partial<FeatureStore>): Promise<FeatureStore> => {
    const res = await apiClient.post('/api/v1/analytics/features', data);
    return res.data;
  },

  // ML Models & Registry
  getModels: async (orgId: string): Promise<MLModel[]> => {
    const res = await apiClient.get('/api/v1/analytics/models', { params: { org_id: orgId } });
    return res.data;
  },

  registerModel: async (data: Partial<MLModel>): Promise<MLModel> => {
    const res = await apiClient.post('/api/v1/analytics/models', data);
    return res.data;
  },

  // Prediction Sandbox
  runOnlinePrediction: async (modelVersionId: string, inputData: any): Promise<PredictionResult> => {
    const res = await apiClient.post('/api/v1/analytics/predictions/online', {
      model_version_id: modelVersionId,
      input_data: inputData,
    });
    return res.data;
  },

  // Drift Monitoring
  generateDriftReport: async (modelId: string, driftType: string): Promise<DriftReport> => {
    const res = await apiClient.post('/api/v1/analytics/drift/reports', {
      model_id: modelId,
      drift_type: driftType,
    });
    return res.data;
  },
};
