import { apiClient as api } from './apiClient';

export interface DatasetItem {
  id: string;
  code: string;
  name: string;
  description: string;
  domain: string;
  format: string;
  status: string;
  row_count: number;
  file_size_bytes: number;
  target_column: string;
  features: string[];
  lineage_json: any;
  tags: string[];
  created_at: string;
  versions: any[];
}

export interface NotebookItem {
  id: string;
  code: string;
  title: string;
  description: string;
  language: string;
  author: string;
  runtime_env: string;
  status: string;
  cells_json: any[];
  execution_logs: any[];
  version: string;
  updated_at: string;
}

export interface RegisteredModelItem {
  id: string;
  model_code: string;
  name: string;
  description: string;
  model_type: string;
  ml_framework: string;
  business_domain: string;
  target_column: string;
  current_version: string;
  stage: string;
  approval_status: string;
  approval_notes: string;
  approved_by: string;
  approved_at: string;
  metadata_json: any;
  tags: string[];
  created_at: string;
  artifacts?: any[];
}

export interface EvaluationReportItem {
  id: string;
  model_id: string;
  model_version: string;
  evaluation_name: string;
  roc_curve_json: any;
  precision_recall_curve_json: any;
  confusion_matrix_json: any;
  regression_metrics_json: any;
  feature_importance_json: any;
  learning_curve_json: any;
  calibration_curve_json: any;
  created_at: string;
}

export interface ExplainabilityReportItem {
  id: string;
  model_id: string;
  model_version: string;
  shap_data_json: any;
  lime_data_json: any;
  permutation_importance_json: any;
  global_explanation_json: any;
  local_explanation_json: any;
  created_at: string;
}

export interface ModelComparisonResponse {
  compared_models: any[];
  winner_by_accuracy: string;
  winner_by_latency: string;
}

export const mlStudioService = {
  // Datasets
  async getDatasets(domain?: string): Promise<DatasetItem[]> {
    const res = await api.get('/ml-studio/datasets', { params: { domain } });
    return res.data;
  },
  async createDataset(data: any): Promise<DatasetItem> {
    const res = await api.post('/ml-studio/datasets', data);
    return res.data;
  },
  async getDatasetPreview(id: string): Promise<any> {
    const res = await api.get(`/ml-studio/datasets/${id}/preview`);
    return res.data;
  },
  async validateDataset(id: string): Promise<any> {
    const res = await api.post(`/ml-studio/datasets/${id}/validate`);
    return res.data;
  },

  // Notebooks
  async getNotebooks(): Promise<NotebookItem[]> {
    const res = await api.get('/ml-studio/notebooks');
    return res.data;
  },
  async createNotebook(data: any): Promise<NotebookItem> {
    const res = await api.post('/ml-studio/notebooks', data);
    return res.data;
  },
  async executeNotebook(id: string): Promise<any> {
    const res = await api.post(`/ml-studio/notebooks/${id}/execute`);
    return res.data;
  },
  async getNotebookTemplates(): Promise<any[]> {
    const res = await api.get('/ml-studio/notebooks/templates');
    return res.data;
  },

  // Models & Approval Workflow
  async getModels(stage?: string): Promise<RegisteredModelItem[]> {
    const res = await api.get('/ml-studio/models', { params: { stage } });
    return res.data;
  },
  async registerModel(data: any): Promise<RegisteredModelItem> {
    const res = await api.post('/ml-studio/models', data);
    return res.data;
  },
  async approveModel(id: string, approval_status: string, approved_by: string, approval_notes?: string): Promise<RegisteredModelItem> {
    const res = await api.post(`/ml-studio/models/${id}/approve`, {
      approval_status,
      approved_by,
      approval_notes,
    });
    return res.data;
  },
  async promoteModel(id: string, stage: string): Promise<RegisteredModelItem> {
    const res = await api.post(`/ml-studio/models/${id}/promote`, { stage });
    return res.data;
  },

  // Evaluation & Explainability
  async getEvaluationReport(modelId: string): Promise<EvaluationReportItem[]> {
    const res = await api.get(`/ml-studio/evaluations/${modelId}`);
    return res.data;
  },
  async getExplainabilityReport(modelId: string): Promise<ExplainabilityReportItem[]> {
    const res = await api.get(`/ml-studio/explainability/${modelId}`);
    return res.data;
  },
  async explainLocalPrediction(data: any): Promise<any> {
    const res = await api.post('/ml-studio/explainability/local-explain', data);
    return res.data;
  },

  // Comparison & Packaging
  async compareModels(): Promise<ModelComparisonResponse> {
    const res = await api.get('/ml-studio/models/compare');
    return res.data;
  },
  async preparePackaging(modelId: string): Promise<any> {
    const res = await api.post(`/ml-studio/packaging/${modelId}/prepare`);
    return res.data;
  },
};
