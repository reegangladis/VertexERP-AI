import { apiClient } from './apiClient';

export interface BOMItem {
  id?: string;
  raw_material_id: string;
  quantity: number;
  unit: string;
  scrap_percentage: number;
  sequence: number;
}

export interface BillOfMaterial {
  id: string;
  product_id: string;
  version_id?: string;
  bom_code: string;
  revision: string;
  description?: string;
  status: string;
  created_at: string;
  items: BOMItem[];
}

export interface WorkCenter {
  id: string;
  organization_id: string;
  center_name: string;
  center_code: string;
  capacity: number;
  location?: string;
  status: string;
  created_at: string;
}

export interface Machine {
  id: string;
  work_center_id: string;
  machine_name: string;
  machine_code: string;
  manufacturer?: string;
  serial_number?: string;
  status: string;
  created_at: string;
}

export interface ProductionOrder {
  id: string;
  organization_id: string;
  production_number: string;
  product_id: string;
  planned_quantity: number;
  completed_quantity: number;
  scheduled_start: string;
  scheduled_end: string;
  priority: string;
  status: string;
  created_at: string;
}

export interface QualityInspection {
  id: string;
  production_order_id: string;
  inspection_type: string;
  inspection_date: string;
  status: string;
  created_at: string;
}

export interface MRPRecommendation {
  product_id: string;
  product_name: string;
  required_quantity: number;
  current_stock: number;
  shortage_quantity: number;
  action_type: string;
}

export interface MRPRunResponse {
  id: string;
  organization_id: string;
  run_date: string;
  planning_period: string;
  status: string;
  processed_items: number;
  recommendations: MRPRecommendation[];
  created_at: string;
}

export interface ManufacturingDashboardSummary {
  active_production_orders: number;
  machine_utilization_rate: number;
  total_material_consumed: number;
  production_efficiency_percentage: number;
  total_production_cost: number;
  quality_pass_rate_percentage: number;
  mrp_recommendations_count: number;
  maintenance_schedules_count: number;
}

export const manufacturingMrpService = {
  // Dashboard
  getDashboardSummary: async (orgId: string): Promise<ManufacturingDashboardSummary> => {
    const res = await apiClient.get('/api/v1/manufacturing/dashboard', { params: { org_id: orgId } });
    return res.data;
  },

  // BOM
  getBOMs: async (): Promise<BillOfMaterial[]> => {
    const res = await apiClient.get('/api/v1/manufacturing/bom');
    return res.data;
  },

  createBOM: async (data: any): Promise<BillOfMaterial> => {
    const res = await apiClient.post('/api/v1/manufacturing/bom', data);
    return res.data;
  },

  // Production Orders
  getProductionOrders: async (orgId: string): Promise<ProductionOrder[]> => {
    const res = await apiClient.get('/api/v1/manufacturing/production-orders', { params: { org_id: orgId } });
    return res.data;
  },

  createProductionOrder: async (data: any): Promise<ProductionOrder> => {
    const res = await apiClient.post('/api/v1/manufacturing/production-orders', data);
    return res.data;
  },

  startProductionOrder: async (id: string): Promise<ProductionOrder> => {
    const res = await apiClient.post(`/api/v1/manufacturing/production-orders/${id}/start`);
    return res.data;
  },

  completeProductionOrder: async (id: string): Promise<ProductionOrder> => {
    const res = await apiClient.post(`/api/v1/manufacturing/production-orders/${id}/complete`);
    return res.data;
  },

  // Work Centers & Machines
  getWorkCenters: async (orgId: string): Promise<WorkCenter[]> => {
    const res = await apiClient.get('/api/v1/manufacturing/work-centers', { params: { org_id: orgId } });
    return res.data;
  },

  getMachines: async (): Promise<Machine[]> => {
    const res = await apiClient.get('/api/v1/manufacturing/machines');
    return res.data;
  },

  // MRP
  runMRP: async (orgId: string, period: string): Promise<MRPRunResponse> => {
    const res = await apiClient.post('/api/v1/manufacturing/mrp/run', {
      organization_id: orgId,
      planning_period: period,
    });
    return res.data;
  },

  // Quality
  getQualityInspections: async (): Promise<QualityInspection[]> => {
    const res = await apiClient.get('/api/v1/manufacturing/quality');
    return res.data;
  },
};
