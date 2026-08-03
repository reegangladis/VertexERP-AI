import React, { useEffect, useState } from 'react';
import {
  Package,
  Boxes,
  Truck,
  TrendingDown,
  AlertTriangle,
  Plus,
  ArrowRightLeft,
  DollarSign,
  Building,
  CheckCircle2,
  FileCheck,
  RefreshCw,
  Search,
  SlidersHorizontal,
} from 'lucide-react';
import {
  inventoryProcurementService,
  InventoryDashboardSummary,
  Product,
  Warehouse,
  StockLevel,
  Supplier,
  PurchaseOrder,
} from '../../services/inventoryProcurement';

export function InventoryModule() {
  const [activeTab, setActiveTab] = useState<
    'dashboard' | 'products' | 'warehouses' | 'stock' | 'purchases' | 'suppliers'
  >('dashboard');
  const [loading, setLoading] = useState<boolean>(true);
  const [summary, setSummary] = useState<InventoryDashboardSummary | null>(null);

  const [products, setProducts] = useState<Product[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [stockLevels, setStockLevels] = useState<StockLevel[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([]);

  // Modals & Form States
  const [showProductModal, setShowProductModal] = useState<boolean>(false);
  const [showStockModal, setShowStockModal] = useState<boolean>(false);

  // Form Inputs
  const [sku, setSku] = useState('');
  const [productName, setProductName] = useState('');
  const [costPrice, setCostPrice] = useState(100);
  const [sellingPrice, setSellingPrice] = useState(150);

  const mockOrgId = '00000000-0000-0000-0000-000000000001';

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sumRes, prodRes, whRes, stockRes, suppRes, poRes] = await Promise.all([
        inventoryProcurementService.getDashboardSummary(mockOrgId).catch(() => null),
        inventoryProcurementService.getProducts(mockOrgId).catch(() => []),
        inventoryProcurementService.getWarehouses(mockOrgId).catch(() => []),
        inventoryProcurementService.getStockLevels().catch(() => []),
        inventoryProcurementService.getSuppliers(mockOrgId).catch(() => []),
        inventoryProcurementService.getPurchaseOrders().catch(() => []),
      ]);

      setSummary(
        sumRes || {
          total_products: prodRes.length,
          total_warehouses: whRes.length,
          total_suppliers: suppRes.length,
          total_stock_value: stockRes.reduce((acc, s) => acc + s.available_quantity * 100, 0),
          low_stock_count: stockRes.filter((s) => s.available_quantity <= s.reorder_quantity && s.available_quantity > 0).length,
          out_of_stock_count: stockRes.filter((s) => s.available_quantity === 0).length,
          pending_purchase_orders: poRes.filter((p) => p.status === 'Draft').length,
          total_goods_received: poRes.filter((p) => p.status === 'Received').length,
        }
      );

      setProducts(prodRes);
      setWarehouses(whRes);
      setStockLevels(stockRes);
      setSuppliers(suppRes);
      setPurchaseOrders(poRes);
    } catch (err) {
      console.error('Failed to load inventory data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await inventoryProcurementService.createProduct({
        organization_id: mockOrgId,
        sku: sku || `SKU-${Math.floor(1000 + Math.random() * 9000)}`,
        product_name: productName,
        cost_price: Number(costPrice),
        selling_price: Number(sellingPrice),
        status: 'Active',
      });
      setShowProductModal(false);
      setProductName('');
      setSku('');
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create product');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans">
      {/* Header */}
      <header className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 shadow-lg shadow-teal-500/30">
              <Boxes className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400">
                Inventory & Procurement Platform
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Multi-Warehouse Stock Control, SKU Catalog, Purchase Orders & Receiving
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowProductModal(true)}
            className="flex items-center gap-2 bg-gradient-to-r from-teal-500 to-emerald-600 hover:from-teal-600 hover:to-emerald-700 text-white px-4 py-2.5 rounded-lg font-medium shadow-md shadow-emerald-500/20 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Add Product
          </button>
        </div>
      </header>

      {/* Tabs */}
      <nav className="flex space-x-2 border-b border-slate-800 mb-8 overflow-x-auto pb-2">
        {[
          { id: 'dashboard', label: 'Overview Dashboard', icon: Boxes },
          { id: 'products', label: 'Product Catalog', icon: Package },
          { id: 'warehouses', label: 'Warehouses', icon: Building },
          { id: 'stock', label: 'Stock Levels & Transfers', icon: ArrowRightLeft },
          { id: 'purchases', label: 'Purchase Orders', icon: FileCheck },
          { id: 'suppliers', label: 'Suppliers', icon: Truck },
        ].map((tab) => {
          const Icon = tab.icon;
          const active = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm transition-all whitespace-nowrap cursor-pointer ${
                active
                  ? 'bg-slate-800 text-emerald-400 border border-slate-700 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </nav>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl relative overflow-hidden">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Total Stock Valuation</span>
                <DollarSign className="w-5 h-5 text-emerald-400" />
              </div>
              <div className="text-3xl font-extrabold text-white">
                ${summary?.total_stock_value.toLocaleString() || '0'}
              </div>
              <p className="text-xs text-slate-400 mt-2">Valued at standard cost</p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl relative overflow-hidden">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Total SKUs</span>
                <Package className="w-5 h-5 text-blue-400" />
              </div>
              <div className="text-3xl font-extrabold text-white">
                {summary?.total_products || 0}
              </div>
              <p className="text-xs text-blue-400 mt-2">Active product catalog items</p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl relative overflow-hidden">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Low Stock Alerts</span>
                <AlertTriangle className="w-5 h-5 text-amber-400" />
              </div>
              <div className="text-3xl font-extrabold text-amber-400">
                {summary?.low_stock_count || 0}
              </div>
              <p className="text-xs text-slate-400 mt-2">Items below reorder point</p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl relative overflow-hidden">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Active Warehouses</span>
                <Building className="w-5 h-5 text-purple-400" />
              </div>
              <div className="text-3xl font-extrabold text-white">
                {summary?.total_warehouses || 0}
              </div>
              <p className="text-xs text-purple-400 mt-2">Distribution hubs</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
              <h3 className="text-lg font-bold text-white mb-4">Pending Purchase Orders</h3>
              <div className="space-y-3">
                {purchaseOrders.length === 0 ? (
                  <p className="text-slate-500 text-sm">No pending purchase orders.</p>
                ) : (
                  purchaseOrders.slice(0, 5).map((po) => (
                    <div key={po.id} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                      <div>
                        <div className="font-mono text-emerald-400 font-bold">{po.purchase_order_number}</div>
                        <div className="text-xs text-slate-400 mt-0.5">Order Date: {po.order_date}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-white">${po.grand_total.toLocaleString()}</div>
                        <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-medium">{po.status}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
              <h3 className="text-lg font-bold text-white mb-4">Active Suppliers Directory</h3>
              <div className="space-y-3">
                {suppliers.length === 0 ? (
                  <p className="text-slate-500 text-sm">No suppliers registered.</p>
                ) : (
                  suppliers.slice(0, 5).map((supp) => (
                    <div key={supp.id} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                      <div>
                        <div className="font-semibold text-slate-200">{supp.company_name}</div>
                        <div className="text-xs text-slate-400">{supp.email}</div>
                      </div>
                      <span className="text-xs font-mono text-indigo-400 font-bold">{supp.supplier_code}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Products Tab */}
      {activeTab === 'products' && (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white">Product Catalog & SKUs</h3>
            <button
              onClick={() => setShowProductModal(true)}
              className="bg-emerald-600 hover:bg-emerald-700 text-white px-3.5 py-2 rounded-lg text-sm font-medium cursor-pointer"
            >
              + Add New Product
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-xs">
                <tr>
                  <th className="p-3.5">SKU</th>
                  <th className="p-3.5">Product Name</th>
                  <th className="p-3.5">Cost Price</th>
                  <th className="p-3.5">Selling Price</th>
                  <th className="p-3.5">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {products.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-6 text-center text-slate-500">
                      No products registered. Click "Add New Product" to populate catalog.
                    </td>
                  </tr>
                ) : (
                  products.map((p) => (
                    <tr key={p.id} className="hover:bg-slate-800/40">
                      <td className="p-3.5 font-mono text-emerald-400 font-bold">{p.sku}</td>
                      <td className="p-3.5 font-semibold text-slate-100">{p.product_name}</td>
                      <td className="p-3.5 text-slate-300">${p.cost_price.toLocaleString()}</td>
                      <td className="p-3.5 text-emerald-400 font-bold">${p.selling_price.toLocaleString()}</td>
                      <td className="p-3.5">
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                          {p.status}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add Product Modal */}
      {showProductModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-4">Add Product to Catalog</h3>
            <form onSubmit={handleCreateProduct} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-400">SKU Code</label>
                <input
                  type="text"
                  placeholder="e.g. SKU-1002"
                  value={sku}
                  onChange={(e) => setSku(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400">Product Name</label>
                <input
                  type="text"
                  required
                  value={productName}
                  onChange={(e) => setProductName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-slate-400">Cost Price ($)</label>
                  <input
                    type="number"
                    value={costPrice}
                    onChange={(e) => setCostPrice(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400">Selling Price ($)</label>
                  <input
                    type="number"
                    value={sellingPrice}
                    onChange={(e) => setSellingPrice(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowProductModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-semibold cursor-pointer"
                >
                  Save Product
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
