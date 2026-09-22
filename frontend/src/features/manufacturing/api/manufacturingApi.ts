import { apiClient } from "@/lib/api-client";
import {
  BillOfMaterial,
  BOMComponent,
  BOMVersion,
  Machine,
  MaterialConsumption,
  MRPPlannedOrder,
  MRPRun,
  ProductionOrder,
  ProductionOutput,
  ProductionScrap,
  QualityInspection,
  Routing,
  RoutingOperation,
  WorkCenter,
} from "../types";

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export const manufacturingApi = {
  // Work Centers & Machines
  getWorkCenters: (params?: { work_center_type?: string; status?: string; page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.work_center_type) q.set("work_center_type", params.work_center_type);
    if (params?.status) q.set("status", params.status);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<WorkCenter>>(`/manufacturing/work-centers?${q.toString()}`);
  },
  createWorkCenter: (data: Partial<WorkCenter>) =>
    apiClient<WorkCenter>("/manufacturing/work-centers", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getWorkCenterById: (id: string) => apiClient<WorkCenter>(`/manufacturing/work-centers/${id}`),
  updateWorkCenter: (id: string, data: Partial<WorkCenter>) =>
    apiClient<WorkCenter>(`/manufacturing/work-centers/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  createMachine: (data: Partial<Machine>) =>
    apiClient<Machine>("/manufacturing/machines", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateMachine: (id: string, data: Partial<Machine>) =>
    apiClient<Machine>(`/manufacturing/machines/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  // Routings & Operations
  getRoutings: (params?: { product_id?: string; page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.product_id) q.set("product_id", params.product_id);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<Routing>>(`/manufacturing/routings?${q.toString()}`);
  },
  createRouting: (data: any) =>
    apiClient<Routing>("/manufacturing/routings", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getRoutingById: (id: string) => apiClient<Routing>(`/manufacturing/routings/${id}`),
  createOperation: (data: Partial<RoutingOperation>) =>
    apiClient<RoutingOperation>("/manufacturing/routing-operations", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Bills of Materials
  getBOMs: (params?: { product_id?: string; status?: string; page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.product_id) q.set("product_id", params.product_id);
    if (params?.status) q.set("status", params.status);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<BillOfMaterial>>(`/manufacturing/boms?${q.toString()}`);
  },
  createBOM: (data: any) =>
    apiClient<BillOfMaterial>("/manufacturing/boms", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getBOMById: (id: string) => apiClient<BillOfMaterial>(`/manufacturing/boms/${id}`),
  createBOMVersion: (bomId: string, data: Partial<BOMVersion>) =>
    apiClient<BOMVersion>(`/manufacturing/boms/${bomId}/versions`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  addBOMComponent: (versionId: string, data: Partial<BOMComponent>) =>
    apiClient<BOMComponent>(`/manufacturing/bom-versions/${versionId}/components`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  calculateBOMCost: (versionId: string) =>
    apiClient<{ bom_version_id: string; theoretical_cost: string }>(
      `/manufacturing/bom-versions/${versionId}/theoretical-cost`
    ),

  // Production Orders & Operations
  getProductionOrders: (params?: { status?: string; priority?: string; page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.status) q.set("status", params.status);
    if (params?.priority) q.set("priority", params.priority);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<ProductionOrder>>(`/manufacturing/production-orders?${q.toString()}`);
  },
  createProductionOrder: (data: any) =>
    apiClient<ProductionOrder>("/manufacturing/production-orders", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getProductionOrderById: (id: string) => apiClient<ProductionOrder>(`/manufacturing/production-orders/${id}`),
  confirmProductionOrder: (id: string) =>
    apiClient<ProductionOrder>(`/manufacturing/production-orders/${id}/confirm`, {
      method: "POST",
    }),
  completeProductionOrder: (id: string) =>
    apiClient<ProductionOrder>(`/manufacturing/production-orders/${id}/complete`, {
      method: "POST",
    }),
  cancelProductionOrder: (id: string) =>
    apiClient<ProductionOrder>(`/manufacturing/production-orders/${id}/cancel`, {
      method: "POST",
    }),
  updateWorkOrderStatus: (workOrderId: string, status: string, actual_duration_hours?: number) =>
    apiClient<any>(`/manufacturing/work-orders/${workOrderId}/status`, {
      method: "POST",
      body: JSON.stringify({ status, actual_duration_hours }),
    }),
  recordMaterialConsumption: (orderId: string, data: any) =>
    apiClient<MaterialConsumption>(`/manufacturing/production-orders/${orderId}/consume-materials`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  recordProductionOutput: (orderId: string, data: any) =>
    apiClient<ProductionOutput>(`/manufacturing/production-orders/${orderId}/record-output`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  recordProductionScrap: (orderId: string, data: any) =>
    apiClient<ProductionScrap>(`/manufacturing/production-orders/${orderId}/record-scrap`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // MRP Engine
  getMRPRuns: (params?: { page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<MRPRun>>(`/manufacturing/mrp/runs?${q.toString()}`);
  },
  executeMRPRun: (planning_horizon_days: number = 30) =>
    apiClient<MRPRun>("/manufacturing/mrp/runs", {
      method: "POST",
      body: JSON.stringify({ planning_horizon_days }),
    }),
  getMRPRunById: (id: string) => apiClient<MRPRun>(`/manufacturing/mrp/runs/${id}`),
  convertPlannedOrder: (plannedOrderId: string) =>
    apiClient<{ converted_type: string; document_id: string; number: string }>(
      `/manufacturing/mrp/planned-orders/${plannedOrderId}/convert`,
      { method: "POST" }
    ),

  // Quality Inspections
  getQualityInspections: (params?: { production_order_id?: string; inspection_type?: string; result?: string; page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.production_order_id) q.set("production_order_id", params.production_order_id);
    if (params?.inspection_type) q.set("inspection_type", params.inspection_type);
    if (params?.result) q.set("result", params.result);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<QualityInspection>>(`/manufacturing/quality-inspections?${q.toString()}`);
  },
  createQualityInspection: (data: any) =>
    apiClient<QualityInspection>("/manufacturing/quality-inspections", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getQualityInspectionById: (id: string) =>
    apiClient<QualityInspection>(`/manufacturing/quality-inspections/${id}`),
};
