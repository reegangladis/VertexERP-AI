import { apiClient } from "@/lib/api-client";
import { PaginatedResponse } from "@/features/inventory/api/inventoryApi";
import { PurchaseOrder, PurchaseRequest, Supplier } from "../types";

export const procurementApi = {
  // Suppliers
  getSuppliers: (params?: { page?: number; page_size?: number; search?: string; status?: string }) => {
    const q = new URLSearchParams();
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    if (params?.search) q.set("search", params.search);
    if (params?.status) q.set("status", params.status);
    const qs = q.toString();
    return apiClient<PaginatedResponse<Supplier>>(`/procurement/suppliers${qs ? `?${qs}` : ""}`);
  },
  getSupplier: (id: string) => apiClient<Supplier>(`/procurement/suppliers/${id}`),
  createSupplier: (data: Partial<Supplier>) =>
    apiClient<Supplier>("/procurement/suppliers", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Purchase Requests
  getPurchaseRequests: (params?: { page?: number; page_size?: number; status?: string }) => {
    const q = new URLSearchParams();
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    if (params?.status) q.set("status", params.status);
    const qs = q.toString();
    return apiClient<PaginatedResponse<PurchaseRequest>>(`/procurement/requests${qs ? `?${qs}` : ""}`);
  },
  getPurchaseRequest: (id: string) => apiClient<PurchaseRequest>(`/procurement/requests/${id}`),
  createPurchaseRequest: (data: Partial<PurchaseRequest>) =>
    apiClient<PurchaseRequest>("/procurement/requests", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  submitPurchaseRequest: (id: string) =>
    apiClient<PurchaseRequest>(`/procurement/requests/${id}/submit`, { method: "POST" }),
  approvePurchaseRequest: (id: string) =>
    apiClient<PurchaseRequest>(`/procurement/requests/${id}/approve`, { method: "POST" }),
  rejectPurchaseRequest: (id: string, reason: string) =>
    apiClient<PurchaseRequest>(`/procurement/requests/${id}/reject`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),

  // Purchase Orders
  getPurchaseOrders: (params?: { page?: number; page_size?: number; status?: string; supplier_id?: string }) => {
    const q = new URLSearchParams();
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    if (params?.status) q.set("status", params.status);
    if (params?.supplier_id) q.set("supplier_id", params.supplier_id);
    const qs = q.toString();
    return apiClient<PaginatedResponse<PurchaseOrder>>(`/procurement/orders${qs ? `?${qs}` : ""}`);
  },
  getPurchaseOrder: (id: string) => apiClient<PurchaseOrder>(`/procurement/orders/${id}`),
  createPurchaseOrder: (data: Partial<PurchaseOrder>) =>
    apiClient<PurchaseOrder>("/procurement/orders", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  issuePurchaseOrder: (id: string) =>
    apiClient<PurchaseOrder>(`/procurement/orders/${id}/issue`, { method: "POST" }),
  confirmPurchaseOrder: (id: string) =>
    apiClient<PurchaseOrder>(`/procurement/orders/${id}/confirm`, { method: "POST" }),
  cancelPurchaseOrder: (id: string, reason: string) =>
    apiClient<PurchaseOrder>(`/procurement/orders/${id}/cancel`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),
};
