import { apiClient } from './apiClient';

export interface ProductCategory {
  id: string;
  organization_id: string;
  category_name: string;
  category_code: string;
  description?: string;
  created_at: string;
}

export interface Brand {
  id: string;
  organization_id: string;
  brand_name: string;
  description?: string;
  created_at: string;
}

export interface UnitOfMeasure {
  id: string;
  organization_id: string;
  unit_name: string;
  unit_code: string;
  created_at: string;
}

export interface Product {
  id: string;
  organization_id: string;
  category_id?: string;
  brand_id?: string;
  unit_id?: string;
  sku: string;
  barcode?: string;
  product_name: string;
  description?: string;
  cost_price: number;
  selling_price: number;
  minimum_stock: number;
  maximum_stock: number;
  reorder_level: number;
  track_inventory: boolean;
  status: string;
  created_at: string;
}

export interface Warehouse {
  id: string;
  organization_id: string;
  warehouse_name: string;
  warehouse_code: string;
  status: string;
  created_at: string;
}

export interface StockLevel {
  id: string;
  warehouse_id: string;
  product_id: string;
  available_quantity: number;
  reserved_quantity: number;
  damaged_quantity: number;
  reorder_quantity: number;
  created_at: string;
}

export interface Supplier {
  id: string;
  organization_id: string;
  supplier_code: string;
  company_name: string;
  email: string;
  phone?: string;
  payment_terms: string;
  status: string;
  created_at: string;
}

export interface PurchaseOrderItem {
  id?: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  tax_amount: number;
  total_price?: number;
}

export interface PurchaseOrder {
  id: string;
  supplier_id: string;
  purchase_order_number: string;
  order_date: string;
  expected_delivery: string;
  subtotal: number;
  tax: number;
  discount: number;
  grand_total: number;
  status: string;
  created_at: string;
  items: PurchaseOrderItem[];
}

export interface InventoryDashboardSummary {
  total_products: number;
  total_warehouses: number;
  total_suppliers: number;
  total_stock_value: number;
  low_stock_count: number;
  out_of_stock_count: number;
  pending_purchase_orders: number;
  total_goods_received: number;
}

export const inventoryProcurementService = {
  // Dashboard
  getDashboardSummary: async (orgId: string): Promise<InventoryDashboardSummary> => {
    const res = await apiClient.get('/api/v1/inventory/dashboard', { params: { org_id: orgId } });
    return res.data;
  },

  // Categories & Brands
  getCategories: async (orgId: string): Promise<ProductCategory[]> => {
    const res = await apiClient.get('/api/v1/inventory/categories', { params: { org_id: orgId } });
    return res.data;
  },

  getBrands: async (orgId: string): Promise<Brand[]> => {
    const res = await apiClient.get('/api/v1/inventory/brands', { params: { org_id: orgId } });
    return res.data;
  },

  getUnits: async (orgId: string): Promise<UnitOfMeasure[]> => {
    const res = await apiClient.get('/api/v1/inventory/units', { params: { org_id: orgId } });
    return res.data;
  },

  // Products
  getProducts: async (orgId: string): Promise<Product[]> => {
    const res = await apiClient.get('/api/v1/inventory/products', { params: { org_id: orgId } });
    return res.data;
  },

  createProduct: async (data: Partial<Product>): Promise<Product> => {
    const res = await apiClient.post('/api/v1/inventory/products', data);
    return res.data;
  },

  // Warehouses & Stock
  getWarehouses: async (orgId: string): Promise<Warehouse[]> => {
    const res = await apiClient.get('/api/v1/inventory/warehouses', { params: { org_id: orgId } });
    return res.data;
  },

  createWarehouse: async (data: Partial<Warehouse>): Promise<Warehouse> => {
    const res = await apiClient.post('/api/v1/inventory/warehouses', data);
    return res.data;
  },

  getStockLevels: async (warehouseId?: string): Promise<StockLevel[]> => {
    const res = await apiClient.get('/api/v1/inventory/stock-levels', { params: { warehouse_id: warehouseId } });
    return res.data;
  },

  adjustStock: async (data: any): Promise<StockLevel> => {
    const res = await apiClient.post('/api/v1/inventory/stock-adjustments', data);
    return res.data;
  },

  transferStock: async (data: any): Promise<any> => {
    const res = await apiClient.post('/api/v1/inventory/stock-transfers', data);
    return res.data;
  },

  // Suppliers
  getSuppliers: async (orgId: string): Promise<Supplier[]> => {
    const res = await apiClient.get('/api/v1/inventory/suppliers', { params: { org_id: orgId } });
    return res.data;
  },

  createSupplier: async (data: Partial<Supplier>): Promise<Supplier> => {
    const res = await apiClient.post('/api/v1/inventory/suppliers', data);
    return res.data;
  },

  // Purchase Orders & Receiving
  getPurchaseOrders: async (supplierId?: string): Promise<PurchaseOrder[]> => {
    const res = await apiClient.get('/api/v1/inventory/purchase-orders', { params: { supplier_id: supplierId } });
    return res.data;
  },

  createPurchaseOrder: async (data: any): Promise<PurchaseOrder> => {
    const res = await apiClient.post('/api/v1/inventory/purchase-orders', data);
    return res.data;
  },

  receiveGoods: async (data: any): Promise<any> => {
    const res = await apiClient.post('/api/v1/inventory/goods-receipts', data);
    return res.data;
  },
};
