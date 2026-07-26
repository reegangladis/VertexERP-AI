import { apiClient } from './apiClient';

export interface MLModel {
  id: string;
  organization_id: string;
  model_code: string;
  name: string;
  description?: string;
  model_type: string;
  ml_framework: string;
  business_domain: string;
  target_column?: string;
  feature_names: string[];
  status: string;
  metadata_json?: Record<string, any>;
  created_at: string;
  updated_at: string;
  versions?: ModelVersion[];
}

export interface ModelVersion {
  id: string;
  model_id: string;
  version: string;
  status: string;
  hyperparameters?: Record<string, any>;
  metrics_json?: Record<string, any>;
  artifact_path?: string;
  approval_status: string;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
}

export interface MLTrainingJob {
  id: string;
  organization_id: string;
  model_id?: string;
  job_name: string;
  model_type: string;
  ml_framework: string;
  dataset_name: string;
  hyperparameters_json?: Record<string, any>;
  status: string;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

export interface MLPrediction {
  id: string;
  organization_id: string;
  model_version_id?: string;
  prediction_type: string;
  business_module?: string;
  input_data_json: Record<string, any>;
  output_data_json: Record<string, any>;
  confidence_score?: number;
  latency_ms: number;
  status: string;
  created_at: string;
}

export interface MLExperiment {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  model_type: string;
  target_column?: string;
  status: string;
  created_at: string;
  updated_at: string;
  runs?: MLExperimentRun[];
}

export interface MLExperimentRun {
  id: string;
  experiment_id: string;
  run_name: string;
  parameters_json?: Record<string, any>;
  metrics_json?: Record<string, any>;
  artifacts_metadata_json?: Record<string, any>;
  training_history_json?: Record<string, any>[];
  status: string;
  duration_seconds: number;
  created_at: string;
}

export interface MLEvaluationMetric {
  id: string;
  model_version_id: string;
  run_id?: string;
  metric_name: string;
  metric_value: number;
  dataset_type: string;
  metadata_json?: Record<string, any>;
  confusion_matrix_json?: Record<string, any>;
  feature_importance_json?: Record<string, any>;
  created_at: string;
}

export interface BusinessModulePredictResponse {
  module_key: string;
  prediction_result: Record<string, any>;
  confidence_score: number;
  risk_level?: string;
  recommendations: string[];
  latency_ms: number;
}

export const mlService = {
  // Model Registry
  async getModels(): Promise<MLModel[]> {
    const res = await apiClient.get('/api/v1/ml/models');
    return res.data;
  },

  async createModel(data: Partial<MLModel>): Promise<MLModel> {
    const res = await apiClient.post('/api/v1/ml/models', data);
    return res.data;
  },

  async createModelVersion(modelId: string, data: { version: string; hyperparameters?: any }): Promise<ModelVersion> {
    const res = await apiClient.post(`/api/v1/ml/models/${modelId}/versions`, data);
    return res.data;
  },

  async approveModelVersion(versionId: string, approvedBy: string): Promise<ModelVersion> {
    const res = await apiClient.post(`/api/v1/ml/versions/${versionId}/approve`, { approved_by: approvedBy });
    return res.data;
  },

  // Training Jobs
  async getTrainingJobs(): Promise<MLTrainingJob[]> {
    const res = await apiClient.get('/api/v1/ml/training-jobs');
    return res.data;
  },

  async createTrainingJob(data: any): Promise<MLTrainingJob> {
    const res = await apiClient.post('/api/v1/ml/training-jobs', data);
    return res.data;
  },

  async executeTrainingJob(jobId: string): Promise<MLTrainingJob> {
    const res = await apiClient.post(`/api/v1/ml/training-jobs/${jobId}/execute`);
    return res.data;
  },

  // Inference & Predictions
  async predictRealtime(data: { model_code?: string; business_module?: string; input_data: any }): Promise<MLPrediction> {
    const res = await apiClient.post('/api/v1/ml/inference/predict', data);
    return res.data;
  },

  async predictBatch(data: { model_code?: string; business_module?: string; batch_input_data: any[] }): Promise<MLPrediction[]> {
    const res = await apiClient.post('/api/v1/ml/inference/predict-batch', data);
    return res.data;
  },

  async getPredictionHistory(): Promise<MLPrediction[]> {
    const res = await apiClient.get('/api/v1/ml/inference/history');
    return res.data;
  },

  // Experiments
  async getExperiments(): Promise<MLExperiment[]> {
    const res = await apiClient.get('/api/v1/ml/experiments');
    return res.data;
  },

  async createExperiment(data: any): Promise<MLExperiment> {
    const res = await apiClient.post('/api/v1/ml/experiments', data);
    return res.data;
  },

  async createExperimentRun(experimentId: string, data: any): Promise<MLExperimentRun> {
    const res = await apiClient.post(`/api/v1/ml/experiments/${experimentId}/runs`, data);
    return res.data;
  },

  // Business Modules Inference
  async predictBusinessModule(moduleKey: string, inputData: any): Promise<BusinessModulePredictResponse> {
    const res = await apiClient.post('/api/v1/ml/business-modules/predict', {
      module_key: moduleKey,
      input_data: inputData,
    });
    return res.data;
  },
};
