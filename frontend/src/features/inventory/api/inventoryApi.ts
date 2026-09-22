import { apiClient } from "@/lib/api-client";
import {
  GoodsReceipt,
  Location,
  Product,
  ProductCategory,
  StockAdjustment,
  StockBalance,
  StockMovement,
  StockTransfer,
  UnitOfMeasure,
  Warehouse,
} from "../types";

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export const inventoryApi = {
  // UOMs
  getUOMs: () => apiClient<PaginatedResponse<UnitOfMeasure>>("/inventory/uom/"),
  createUOM: (data: Partial<UnitOfMeasure>) =>
    apiClient<UnitOfMeasure>("/inventory/uom/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Categories
  getCategories: () => apiClient<PaginatedResponse<ProductCategory>>("/inventory/categories/"),
  createCategory: (data: Partial<ProductCategory>) =>
    apiClient<ProductCategory>("/inventory/categories/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Products
  getProducts: (params?: { page?: number; page_size?: number; search?: string; category_id?: string }) => {
    const q = new URLSearchParams();
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    if (params?.search) q.set("search", params.search);
    if (params?.category_id) q.set("category_id", params.category_id);
    return apiClient<PaginatedResponse<Product>>(`/inventory/products/?${q.toString()}`);
  },
  getProduct: (id: string) => apiClient<Product>(`/inventory/products/${id}`),
  createProduct: (data: Partial<Product>) =>
    apiClient<Product>("/inventory/products/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Warehouses
  getWarehouses: (params?: { page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<Warehouse>>(`/inventory/warehouses/?${q.toString()}`);
  },
  getWarehouse: (id: string) => apiClient<Warehouse>(`/inventory/warehouses/${id}`),
  createWarehouse: (data: Partial<Warehouse>) =>
    apiClient<Warehouse>("/inventory/warehouses/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getWarehouseLocations: (warehouseId: string) =>
    apiClient<Location[]>(`/inventory/warehouses/${warehouseId}/locations`),
  createWarehouseLocation: (warehouseId: string, data: Partial<Location>) =>
    apiClient<Location>(`/inventory/warehouses/${warehouseId}/locations`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Stock Balances & Movements
  getStockBalances: (params?: { warehouse_id?: string; product_id?: string; page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.warehouse_id) q.set("warehouse_id", params.warehouse_id);
    if (params?.product_id) q.set("product_id", params.product_id);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<StockBalance>>(`/inventory/ledger/balances?${q.toString()}`);
  },
  getStockMovements: (params?: { warehouse_id?: string; product_id?: string; page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.warehouse_id) q.set("warehouse_id", params.warehouse_id);
    if (params?.product_id) q.set("product_id", params.product_id);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<StockMovement>>(`/inventory/ledger/movements?${q.toString()}`);
  },

  // Stock Transfers
  getTransfers: (params?: { status?: string; page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.status) q.set("status", params.status);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<StockTransfer>>(`/inventory/transfers/?${q.toString()}`);
  },
  getTransfer: (id: string) => apiClient<StockTransfer>(`/inventory/transfers/${id}`),
  createTransfer: (data: Partial<StockTransfer>) =>
    apiClient<StockTransfer>("/inventory/transfers/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  dispatchTransfer: (id: string, data?: { tracking_number?: string }) =>
    apiClient<StockTransfer>(`/inventory/transfers/${id}/dispatch`, {
      method: "POST",
      body: JSON.stringify(data || {}),
    }),
  receiveTransfer: (id: string, items: Array<{ item_id: string; received_quantity: number }>) =>
    apiClient<StockTransfer>(`/inventory/transfers/${id}/receive`, {
      method: "POST",
      body: JSON.stringify({ items }),
    }),

  // Stock Adjustments
  getAdjustments: (params?: { status?: string; page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.status) q.set("status", params.status);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<StockAdjustment>>(`/inventory/adjustments/?${q.toString()}`);
  },
  getAdjustment: (id: string) => apiClient<StockAdjustment>(`/inventory/adjustments/${id}`),
  createAdjustment: (data: Partial<StockAdjustment>) =>
    apiClient<StockAdjustment>("/inventory/adjustments/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  submitAdjustment: (id: string) =>
    apiClient<StockAdjustment>(`/inventory/adjustments/${id}/submit`, { method: "POST" }),
  approveAdjustment: (id: string) =>
    apiClient<StockAdjustment>(`/inventory/adjustments/${id}/approve`, { method: "POST" }),
  rejectAdjustment: (id: string, reason: string) =>
    apiClient<StockAdjustment>(`/inventory/adjustments/${id}/reject`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),
  postAdjustment: (id: string) =>
    apiClient<StockAdjustment>(`/inventory/adjustments/${id}/post`, { method: "POST" }),

  // Goods Receipts
  getGoodsReceipts: (params?: { status?: string; page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.status) q.set("status", params.status);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<GoodsReceipt>>(`/inventory/receipts/?${q.toString()}`);
  },
  getGoodsReceipt: (id: string) => apiClient<GoodsReceipt>(`/inventory/receipts/${id}`),
  createGoodsReceipt: (data: Partial<GoodsReceipt>) =>
    apiClient<GoodsReceipt>("/inventory/receipts/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  postGoodsReceipt: (id: string) =>
    apiClient<GoodsReceipt>(`/inventory/receipts/${id}/post`, { method: "POST" }),
};
